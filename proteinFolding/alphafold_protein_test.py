"""
AlphaFold-inspired structural superposition rendered in Manim.

This scene loads two adenylate kinase structures (1AKE - open state and
4AKE - closed state), aligns their C-alpha traces with the Kabsch
algorithm, and recreates the kind of structural superposition shown in
PDBe-KB documentation. The workflow leans on standard biomolecular
visualization ideas but keeps everything native to Manim for full control.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

import numpy as np
from manim import *

DATA_DIR = Path(__file__).with_name("data")


@dataclass
class ProteinSpec:
    pdb_id: str
    filename: Path
    label: str
    color: ManimColor
    chain: Optional[str] = "A"
    raw_points: Optional[np.ndarray] = None


def parse_ca_coordinates(pdb_file: Path, chain_id: Optional[str] = None) -> np.ndarray:
    """Extract C-alpha atom coordinates from a PDB file."""
    if not pdb_file.exists():
        raise FileNotFoundError(f"PDB file not found: {pdb_file}")

    coords: List[np.ndarray] = []
    with pdb_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = line[:6].strip()
            if record != "ATOM":
                continue

            atom_name = line[12:16].strip()
            if atom_name != "CA":
                continue

            chain = line[21].strip()
            if chain_id and chain_id != chain:
                continue

            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                continue

            coords.append(np.array([x, y, z], dtype=float))

    return np.array(coords)


def center_points(points: np.ndarray) -> np.ndarray:
    if points.size == 0:
        return points.copy()
    centroid = np.mean(points, axis=0)
    return points - centroid


def kabsch_align(mobile: np.ndarray, reference: np.ndarray) -> np.ndarray:
    if mobile.size == 0 or reference.size == 0:
        return np.zeros((0, 3))

    n = min(len(mobile), len(reference))
    mob = mobile[:n]
    ref = reference[:n]

    mob_centered = center_points(mob)
    ref_centered = center_points(ref)

    covariance = mob_centered.T @ ref_centered
    U, _, Vt = np.linalg.svd(covariance)
    rotation = Vt.T @ U.T

    if np.linalg.det(rotation) < 0:
        Vt[-1, :] *= -1
        rotation = Vt.T @ U.T

    return mob_centered @ rotation


def align_point_sets(point_sets: Sequence[np.ndarray]) -> List[np.ndarray]:
    """Align multiple point clouds to the first entry using the Kabsch algorithm."""
    aligned: List[np.ndarray] = []
    if not point_sets:
        return aligned

    reference = point_sets[0]
    aligned.append(center_points(reference))

    for mobile in point_sets[1:]:
        aligned.append(kabsch_align(mobile, reference))

    radii = [np.linalg.norm(points, axis=1).max() for points in aligned if len(points) > 0]
    max_radius = max(radii) if radii else 1.0
    scale = 3.2 / max_radius if max_radius else 1.0

    return [points * scale for points in aligned]


def sample_indices(length: int, fractions: Sequence[float]) -> List[int]:
    """Convert fractional positions to valid residue indices."""
    if length <= 0:
        return []
    indices = {max(0, min(length - 1, int(length * frac))) for frac in fractions}
    return sorted(indices)


class ProteinStructureAnimation(ThreeDScene):
    """Structural superposition inspired by PDBe-KB visuals."""

    def construct(self) -> None:
        self.camera.background_color = "#04080f"
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        self.structure_specs = [
            ProteinSpec(
                pdb_id="1AKE",
                filename=DATA_DIR / "1AKE.pdb",
                label="Adenylate Kinase (1AKE) - Open",
                color=BLUE_C,
            ),
            ProteinSpec(
                pdb_id="4AKE",
                filename=DATA_DIR / "4AKE.pdb",
                label="Adenylate Kinase (4AKE) - Closed",
                color=ORANGE,
            ),
        ]

        self.structures = self.prepare_structures(self.structure_specs)
        self.common_length = min((len(entry["points"]) for entry in self.structures), default=0)

        self.intro_scene()
        self.wait(0.5)
        self.build_protein_scene()
        self.wait(0.5)
        self.animate_protein_scene()
        self.wait(0.5)
        self.detail_scene()
        self.wait(0.5)
        self.finale_scene()

    def prepare_structures(self, specs: Sequence[ProteinSpec]) -> List[dict]:
        raw_sets: List[np.ndarray] = []
        for spec in specs:
            coords = parse_ca_coordinates(spec.filename, spec.chain)
            if coords.size == 0:
                raise ValueError(f"No C-alpha atoms found for {spec.pdb_id}")
            spec.raw_points = coords
            raw_sets.append(coords)

        aligned_sets = align_point_sets(raw_sets)
        structures = []
        for spec, aligned in zip(specs, aligned_sets):
            backbone = self.create_backbone_path(aligned, spec.color)
            atoms = self.create_atom_group(aligned, spec.color)
            structures.append(
                {
                    "spec": spec,
                    "points": aligned,
                    "backbone": backbone,
                    "atoms": atoms,
                    "group": VGroup(backbone, atoms),
                }
            )

        self.superposition_group = VGroup(*[entry["group"] for entry in structures])
        return structures

    def create_backbone_path(self, points: np.ndarray, color: ManimColor) -> VMobject:
        if len(points) == 0:
            return VMobject()
        elif len(points) == 1:
            backbone = Dot3D(point=points[0], radius=0.1)
            backbone.set_color(color)
            return backbone
        else:
            # Create a 3D path by connecting points with Line3D segments
            segments = VGroup()
            for i in range(len(points) - 1):
                segment = Line3D(
                    start=points[i],
                    end=points[i + 1],
                    color=color,
                    stroke_width=6
                )
                segments.add(segment)
            return segments

    def create_atom_group(self, points: np.ndarray, color: ManimColor) -> VGroup:
        atoms = VGroup()
        if len(points) == 0:
            return atoms
        for idx in range(0, len(points), 3):
            atom = Sphere(radius=0.07, resolution=(8, 16))
            atom.set_fill(color=color, opacity=0.9)
            atom.set_stroke(color=WHITE, opacity=0.15, width=0.5)
            atom.shift(points[idx])
            atoms.add(atom)
        return atoms

    def create_point_cloud(self, points: np.ndarray, color: ManimColor = GRAY_B) -> VGroup:
        dots = VGroup()
        for idx in range(0, len(points), 2):
            dot = Sphere(radius=0.035, resolution=(6, 12))
            dot.set_fill(color=color, opacity=0.65)
            dot.set_stroke(color=WHITE, opacity=0.1, width=0.3)
            dot.shift(points[idx])
            dots.add(dot)
        return dots

    def create_residue_highlight(self, residue_idx: int) -> VGroup:
        highlight = VGroup()
        for entry in self.structures:
            if residue_idx >= len(entry["points"]):
                continue
            point = entry["points"][residue_idx]
            glow = Sphere(radius=0.15, resolution=(12, 18))
            glow.set_fill(color=entry["spec"].color, opacity=0.35)
            glow.set_stroke(color=entry["spec"].color, opacity=0.6, width=1.0)
            glow.shift(point)
            highlight.add(glow)

        if len(self.structures) >= 2 and residue_idx < len(self.structures[1]["points"]):
            start = self.structures[0]["points"][residue_idx]
            end = self.structures[1]["points"][residue_idx]
            connector = DashedLine3D(start, end, color=YELLOW, dash_length=0.15, stroke_width=2.5)
            highlight.add(connector)
        return highlight

    def compute_rmsd(self) -> float:
        if len(self.structures) < 2:
            return 0.0
        n = min(len(self.structures[0]["points"]), len(self.structures[1]["points"]))
        if n == 0:
            return 0.0
        diffs = self.structures[0]["points"][:n] - self.structures[1]["points"][:n]
        return float(np.sqrt(np.sum(diffs ** 2) / n))

    def intro_scene(self) -> None:
        title = Tex(r"AlphaFold-Style\\Structural Superposition", font_size=68)
        title.set_color_by_gradient(BLUE_C, TEAL_E, YELLOW_C)
        subtitle = Tex(r"Real PDB coordinates (1AKE vs 4AKE)", font_size=36)
        subtitle.set_color(GRAY_C)
        subtitle.next_to(title, DOWN, buff=0.5)

        particles = VGroup(
            *[
                Dot3D(
                    point=np.array([
                        np.random.uniform(-6, 6),
                        np.random.uniform(-4, 4),
                        np.random.uniform(-1, 1),
                    ]),
                    radius=0.05,
                    color=np.random.choice([BLUE_B, GREEN_C, YELLOW_C]),
                ).set_opacity(0.35)
                for _ in range(60)
            ]
        )

        self.play(
            LaggedStart(*[FadeIn(p, scale=0.3) for p in particles], lag_ratio=0.02),
            run_time=2,
        )
        self.play(Write(title), run_time=1.8)
        self.play(FadeIn(subtitle, shift=UP), run_time=1)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(particles), run_time=1)

    def build_protein_scene(self) -> None:
        if not self.structures:
            return
        first = self.structures[0]

        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[-3, 3, 1],
            x_length=6,
            y_length=6,
            z_length=6,
        )
        axes.set_stroke(color=GRAY_D, opacity=0.15)

        title = Text("From coordinates to backbone", font_size=42, color=YELLOW_E)
        title.to_corner(UL)
        label = Text(first["spec"].label, font_size=32, color=first["spec"].color)
        label.to_corner(UR)
        self.add_fixed_in_frame_mobjects(title, label)

        self.play(Create(axes), Write(title), Write(label), run_time=1.8)

        point_cloud = self.create_point_cloud(first["points"], color=GRAY_B)
        self.play(
            LaggedStart(*[FadeIn(dot, scale=0.4) for dot in point_cloud], lag_ratio=0.02),
            run_time=2.4,
        )
        self.play(
            LaggedStart(*[FadeOut(dot) for dot in point_cloud], lag_ratio=0.02),
            run_time=0.9,
        )
        self.play(
            LaggedStart(*[FadeIn(atom, scale=0.3) for atom in first["atoms"]], lag_ratio=0.01),
            run_time=2,
        )
        self.play(Create(first["backbone"]), run_time=2)

        self.wait(1.2)
        self.play(FadeOut(axes), FadeOut(title), FadeOut(label), run_time=1)

    def animate_protein_scene(self) -> None:
        if len(self.structures) < 2:
            return
        second = self.structures[1]

        title = Text("Superposition and alignment", font_size=40, color=YELLOW_E)
        title.to_corner(UL)
        metric_text = Text(
            f"Backbone RMSD ~ {self.compute_rmsd():0.2f} Angstroms",
            font_size=30,
            color=GRAY_B,
        )
        metric_text.to_corner(UR)

        self.add_fixed_in_frame_mobjects(title, metric_text)
        self.play(Write(title), FadeIn(metric_text, shift=DOWN), run_time=1.2)

        second["group"].shift(RIGHT * 4)
        second["group"].set_opacity(0.3)

        self.play(
            LaggedStart(*[FadeIn(atom, scale=0.3) for atom in second["atoms"]], lag_ratio=0.01),
            run_time=1.5,
        )
        self.play(Create(second["backbone"]), run_time=1.8)

        self.begin_ambient_camera_rotation(rate=0.12)
        self.play(
            second["group"].animate.shift(LEFT * 4).set_opacity(1),
            run_time=2.2,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(2)
        self.stop_ambient_camera_rotation()

        self.play(FadeOut(title), FadeOut(metric_text), run_time=0.8)

    def detail_scene(self) -> None:
        if self.common_length == 0:
            return

        title = Text("Flexible motifs highlighted", font_size=40, color=YELLOW_E)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        fractions = [0.2, 0.45, 0.7]
        indices = sample_indices(self.common_length, fractions)
        descriptions = [
            "AMP binding loop",
            "Core beta-sheet hinge",
            "Lid domain twist",
        ]

        for idx, description in zip(indices, descriptions):
            highlight = self.create_residue_highlight(idx)
            label = Text(f"Residue {idx + 1}: {description}", font_size=30, color=WHITE)
            label.to_corner(UR)
            self.add_fixed_in_frame_mobjects(label)

            self.play(FadeIn(highlight, scale=0.4), FadeIn(label, shift=DOWN), run_time=1.2)
            self.play(Indicate(highlight, scale_factor=1.15), run_time=1)
            self.wait(0.5)
            self.play(FadeOut(highlight), FadeOut(label), run_time=0.9)

        self.play(FadeOut(title), run_time=0.8)

    def finale_scene(self) -> None:
        title = Tex(r"Complete\\Protein Superposition", font_size=56)
        title.set_color_by_gradient(BLUE_C, GREEN_D, YELLOW_C)
        title.to_corner(UL)
        footer = Text("The beauty of molecular ensembles", font_size=34, color=GRAY_B)
        footer.to_corner(DL)
        self.add_fixed_in_frame_mobjects(title, footer)

        self.play(Write(title), run_time=1.5)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.play(Rotate(self.superposition_group, angle=TAU, axis=UP), run_time=5)
        self.stop_ambient_camera_rotation()

        flash = Flash(
            self.superposition_group.get_center(),
            color=YELLOW,
            flash_radius=2.6,
            line_length=0.4,
        )
        self.play(FadeIn(footer, shift=UP), flash, run_time=2)
        self.wait(2)
        self.play(FadeOut(title), FadeOut(footer), run_time=1.2)
