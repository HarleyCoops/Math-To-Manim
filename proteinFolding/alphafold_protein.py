"""
Manim scene that renders true protein ribbons from PDB coordinates.

The scene queries the PDBe-KB "best structures" endpoint for the insulin
UniProt accession (P01308), downloads the non-overlapping PDB entries that
cover the largest parts of the sequence, converts the C-alpha traces into
stylized ribbon meshes, and showcases them with artistic lighting and camera
motion. The goal is to mimic the lab-style scaffolding shown in PDBe-KB while
keeping everything inside Manim so the narration remains editable.
"""

from __future__ import annotations

import json
import math
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
from manim import *
from manim import config

# Ensure caching stays enabled and keep plenty of cached segments so
# repeated renders reuse the existing MP4 chunks instead of restarting.
config.disable_caching = False
config.max_files_cached = max(config.max_files_cached, 200)

DATA_DIR = Path(__file__).with_name("data")
DATA_DIR.mkdir(exist_ok=True)

TARGET_UNIPROT = "P01308"  # human insulin
PD_BE_BEST_STRUCTURES_URL = "https://www.ebi.ac.uk/pdbe/graph-api/uniprot/best_structures/{uniprot_id}"
PDB_DOWNLOAD_URL = "https://files.rcsb.org/download/{pdb_id}.pdb"
UNIPROT_SEQUENCE_LENGTH = 110


@dataclass
class ObservedRegion:
    start: int
    end: int

    def length(self) -> int:
        return self.end - self.start + 1


@dataclass
class CoverageEntry:
    pdb_id: str
    chain_id: str
    resolution: Optional[float]
    coverage: float
    experimental_method: str
    observed_regions: List[ObservedRegion]

    def nonredundant_regions(self) -> List[ObservedRegion]:
        regions = sorted(self.observed_regions, key=lambda r: (r.start, r.end))
        merged: List[ObservedRegion] = []
        for region in regions:
            if not merged or region.start > merged[-1].end:
                merged.append(region)
            else:
                merged[-1].end = max(merged[-1].end, region.end)
        return merged

    @property
    def min_residue(self) -> int:
        return min(region.start for region in self.observed_regions)

    @property
    def max_residue(self) -> int:
        return max(region.end for region in self.observed_regions)

    @property
    def residue_span(self) -> int:
        return self.max_residue - self.min_residue + 1

    @property
    def midpoint(self) -> float:
        return (self.min_residue + self.max_residue) / 2


@dataclass
class ResiduePoint:
    residue_number: int
    point: np.ndarray


@dataclass
class ChainGeometry:
    entry: CoverageEntry
    raw_points: np.ndarray
    ribbon: VGroup
    spine: VMobject
    atoms: VGroup

    @property
    def group(self) -> VGroup:
        return VGroup(self.ribbon, self.spine, self.atoms)


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url) as handle:
        return json.load(handle)


def fetch_best_structures(uniprot_id: str) -> List[CoverageEntry]:
    data = fetch_json(PD_BE_BEST_STRUCTURES_URL.format(uniprot_id=uniprot_id.lower()))
    entries = []
    for raw in data.get(uniprot_id.upper(), []):
        regions = [
            ObservedRegion(start=item["unp_start"], end=item["unp_end"])
            for item in raw.get("observed_regions", [])
        ]
        resolution = raw.get("resolution")
        if resolution is not None:
            try:
                resolution = float(resolution)
            except ValueError:
                resolution = None
        entries.append(
            CoverageEntry(
                pdb_id=raw["pdb_id"].lower(),
                chain_id=raw["chain_id"].strip(),
                resolution=resolution,
                coverage=float(raw.get("coverage", 0.0)),
                experimental_method=raw.get("experimental_method", "Unknown"),
                observed_regions=regions,
            )
        )
    return entries


def compute_overlap_fraction(candidate: Sequence[ObservedRegion], existing: Sequence[ObservedRegion]) -> float:
    total_length = sum(region.length() for region in candidate)
    if total_length == 0:
        return 0.0

    overlap = 0
    for c in candidate:
        for e in existing:
            start = max(c.start, e.start)
            end = min(c.end, e.end)
            if start <= end:
                overlap += end - start + 1
    return overlap / total_length


def select_non_overlapping(entries: Sequence[CoverageEntry], max_segments: int = 3) -> List[CoverageEntry]:
    sorted_entries = sorted(
        entries,
        key=lambda e: (e.coverage, -(e.resolution or 99.0)),
        reverse=True,
    )
    selected: List[CoverageEntry] = []
    accumulated: List[ObservedRegion] = []

    for entry in sorted_entries:
        overlap_fraction = compute_overlap_fraction(entry.nonredundant_regions(), accumulated)
        new_fraction = entry.coverage * (1 - overlap_fraction)
        if new_fraction < 0.08:
            continue
        selected.append(entry)
        accumulated.extend(entry.nonredundant_regions())
        if len(selected) >= max_segments:
            break
    return selected


def ensure_pdb_file(pdb_id: str) -> Path:
    pdb_path = DATA_DIR / f"{pdb_id}.pdb"
    if pdb_path.exists():
        return pdb_path
    url = PDB_DOWNLOAD_URL.format(pdb_id=pdb_id.upper())
    with urllib.request.urlopen(url) as response:
        pdb_path.write_bytes(response.read())
    return pdb_path


def parse_ca_coordinates(pdb_path: Path, chain_id: str) -> List[ResiduePoint]:
    records: List[ResiduePoint] = []
    with pdb_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if not line.startswith("ATOM"):
                continue
            if line[12:16].strip() != "CA":
                continue
            chain = line[21].strip()
            if chain_id and chain != chain_id:
                continue
            try:
                residue_number = int(line[22:26])
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                continue
            records.append(ResiduePoint(residue_number=residue_number, point=np.array([x, y, z], dtype=float)))
    records.sort(key=lambda item: item.residue_number)
    return records


def points_from_regions(records: Sequence[ResiduePoint], regions: Sequence[ObservedRegion]) -> np.ndarray:
    selected: List[np.ndarray] = []
    for residue in records:
        for region in regions:
            if region.start <= residue.residue_number <= region.end:
                selected.append(residue.point)
                break
    return np.array(selected)


def center_and_scale(points: np.ndarray, target_radius: float = 3.4) -> np.ndarray:
    if len(points) == 0:
        return points
    centered = points - np.mean(points, axis=0)
    radius = np.linalg.norm(centered, axis=1).max()
    scale = target_radius / radius if radius else 1.0
    return centered * scale


def estimate_normals(points: np.ndarray) -> List[np.ndarray]:
    normals: List[np.ndarray] = []
    fallback = np.array([0.0, 0.0, 1.0])
    for i in range(len(points)):
        prev_idx = max(0, i - 1)
        next_idx = min(len(points) - 1, i + 1)
        tangent = points[next_idx] - points[prev_idx]
        if np.linalg.norm(tangent) < 1e-6:
            tangent = np.array([1.0, 0.0, 0.0])
        normal = np.cross(tangent, fallback)
        if np.linalg.norm(normal) < 1e-6:
            normal = np.cross(tangent, np.array([0.0, 1.0, 0.0]))
        norm = np.linalg.norm(normal)
        normals.append(normal / norm if norm else np.array([1.0, 0.0, 0.0]))
    return normals


def build_ribbon_mesh(points: np.ndarray, color: ManimColor, width: float = 0.25) -> VGroup:
    quads = VGroup()
    normals = estimate_normals(points)
    for idx in range(len(points) - 1):
        left_a = points[idx] + normals[idx] * width
        left_b = points[idx + 1] + normals[idx + 1] * width
        right_b = points[idx + 1] - normals[idx + 1] * width
        right_a = points[idx] - normals[idx] * width

        quad = Polygon(left_a, left_b, right_b, right_a, fill_color=color, fill_opacity=0.95, stroke_color=color, stroke_width=0)
        quad.set_shade_in_3d(True)
        quads.add(quad)
    return quads


def build_spine(points: np.ndarray, color: ManimColor) -> VMobject:
    spine = VMobject()
    if len(points) >= 2:
        spine.set_points_smoothly(points)
    elif len(points) == 1:
        spine.set_points(points)
    spine.set_stroke(color=color, width=2, opacity=0.6)
    return spine


def build_atoms(points: np.ndarray, color: ManimColor) -> VGroup:
    atoms = VGroup()
    for point in points[::2]:
        atom = Sphere(radius=0.08, resolution=(12, 24))
        atom.set_fill(color=color, opacity=0.9)
        atom.set_stroke(width=0.5, color=WHITE, opacity=0.2)
        atom.shift(point)
        atoms.add(atom)
    return atoms


def sequence_to_scene_x(residue_index: float, span: float = 8.0) -> float:
    if UNIPROT_SEQUENCE_LENGTH == 0:
        return 0.0
    return ((residue_index / UNIPROT_SEQUENCE_LENGTH) - 0.5) * span


class ProteinStructureAnimation(ThreeDScene):
    """Render insulin scaffolding directly from PDBe coverage segments."""

    def construct(self) -> None:
        self.camera.background_color = "#050914"
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        self.renderer.camera.light_source.move_to(3 * IN + 4 * OUT)

        entries = fetch_best_structures(TARGET_UNIPROT)
        self.selected_entries = select_non_overlapping(entries, max_segments=4)
        self.palette = [TEAL_C, PINK, GOLD, BLUE_C]
        self.chain_geometries = self.prepare_geometries(self.selected_entries)

        self.intro_scene()
        self.sequence_coverage_scene()
        self.build_structure_scene()
        self.finale_scene()

    def prepare_geometries(self, entries: Sequence[CoverageEntry]) -> List[ChainGeometry]:
        geometries: List[ChainGeometry] = []
        for index, entry in enumerate(entries):
            pdb_path = ensure_pdb_file(entry.pdb_id)
            records = parse_ca_coordinates(pdb_path, entry.chain_id)
            points = points_from_regions(records, entry.nonredundant_regions())
            if len(points) < 2:
                continue
            normalized = center_and_scale(points)
            ribbon_color = self.palette[index % len(self.palette)]
            ribbon = build_ribbon_mesh(normalized, color=ribbon_color, width=0.3)
            spine = build_spine(normalized, color=WHITE)
            atoms = build_atoms(normalized, color=ribbon_color)

            chain = ChainGeometry(entry=entry, raw_points=normalized, ribbon=ribbon, spine=spine, atoms=atoms)
            group = chain.group
            group.set_shade_in_3d(True)

            offset = sequence_to_scene_x(entry.midpoint, span=8.5)
            elevation = (index - (len(entries) - 1) / 2) * 0.5
            group.shift(RIGHT * offset + UP * elevation)
            group.rotate(angle=(index * 7) * DEGREES, axis=UP)
            geometries.append(chain)
        return geometries

    def intro_scene(self) -> None:
        title = Tex(r"Insulin structure from PDBe-KB", font_size=64)
        title.set_color_by_gradient(BLUE_C, TEAL_E, GOLD)
        subtitle = Tex(r"UniProt P01308 $\rightarrow$ ribbon meshes", font_size=34, color=GRAY_C)
        subtitle.next_to(title, DOWN, buff=0.5)

        glow = Circle(radius=3, color=TEAL_D, stroke_width=0, fill_opacity=0.25)
        glow.move_to(ORIGIN)

        self.play(FadeIn(glow, scale=0.2), run_time=1.2)
        self.play(Write(title), run_time=1.6)
        self.play(FadeIn(subtitle, shift=UP), run_time=1)
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(glow), run_time=0.8)

    def sequence_coverage_scene(self) -> None:
        axis = NumberLine(x_range=[0, UNIPROT_SEQUENCE_LENGTH, 10], length=8, include_ticks=True, include_numbers=True)
        axis.to_edge(DOWN)
        axis.set_color(GRAY_C)

        labels = VGroup()
        blocks = VGroup()
        for idx, entry in enumerate(self.chain_geometries):
            start = entry.entry.min_residue
            end = entry.entry.max_residue
            width = (end - start) / UNIPROT_SEQUENCE_LENGTH * axis.length
            center_param = (start + end) / 2 / UNIPROT_SEQUENCE_LENGTH * axis.length
            block = RoundedRectangle(width=width, height=0.25, corner_radius=0.08, fill_color=self.palette[idx % len(self.palette)], fill_opacity=0.8, stroke_width=0)
            block.move_to(axis.get_left() + RIGHT * center_param + UP * 0.3)
            label = Tex(f"{entry.entry.pdb_id.upper()}:{entry.entry.chain_id}", font_size=28)
            label.set_color(self.palette[idx % len(self.palette)])
            label.next_to(block, UP, buff=0.1)
            labels.add(label)
            blocks.add(block)

        caption = Text("Non-overlapping PDBe best structures", font_size=32, color=GRAY_A)
        caption.next_to(axis, UP, buff=1.2)

        self.add_fixed_in_frame_mobjects(axis, caption, labels)
        self.play(Write(axis), FadeIn(caption, shift=UP), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(b, scale=0.5) for b in blocks], lag_ratio=0.1), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(label, shift=UP) for label in labels], lag_ratio=0.1), run_time=1)
        self.wait(1)
        self.play(FadeOut(axis), FadeOut(caption), FadeOut(labels), FadeOut(blocks), run_time=0.8)

    def build_structure_scene(self) -> None:
        title = Text("Ribbon scaffolding", font_size=42, color=YELLOW_E)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        for chain in self.chain_geometries:
            label = Text(
                f"{chain.entry.pdb_id.upper()} chain {chain.entry.chain_id} - {chain.entry.experimental_method}",
                font_size=30,
                color=self.palette[self.chain_geometries.index(chain) % len(self.palette)],
            )
            label.to_corner(UR)
            self.add_fixed_in_frame_mobjects(label)
            self.play(FadeIn(chain.group, scale=0.4), FadeIn(label, shift=DOWN), run_time=1.4)
            self.play(Indicate(chain.ribbon, color=WHITE, scale_factor=1.05), run_time=0.8)
            self.wait(0.5)
            self.play(FadeOut(label), run_time=0.6)

        self.play(FadeOut(title), run_time=0.8)

    def finale_scene(self) -> None:
        all_geometry = VGroup(*[chain.group for chain in self.chain_geometries])
        title = Tex(r"Insulin structural collage", font_size=52)
        title.set_color_by_gradient(BLUE_C, GREEN_D, GOLD)
        title.to_corner(UL)
        footer = Text("Data: PDBe-KB best structures", font_size=28, color=GRAY_B)
        footer.to_corner(DL)
        self.add_fixed_in_frame_mobjects(title, footer)

        self.play(Write(title), FadeIn(footer, shift=UP), run_time=1.5)
        self.begin_ambient_camera_rotation(rate=0.18)
        self.play(Rotate(all_geometry, angle=TAU, axis=UP), run_time=6)
        self.stop_ambient_camera_rotation()

        flash = Flash(all_geometry.get_center(), color=YELLOW, flash_radius=2.5, line_length=0.4)
        self.play(flash, run_time=1.5)
        self.wait(2)
        self.play(FadeOut(title), FadeOut(footer), FadeOut(all_geometry), run_time=1.2)
