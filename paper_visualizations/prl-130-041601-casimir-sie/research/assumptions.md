# Assumptions and Caveats for the PRL 130, 041601 Visualization

Purpose: keep the animation scientifically honest. Every item below should appear either as an on-screen caveat label, a narration caveat, or a visual boundary between formal result and modeling approximation.

Primary source: `latex/arxiv_source/Lambda_resubmission.tex` and `research/pdf_text_pages.md`.

## Caveat language policy

Use:
- "The paper models..."
- "Under this approximation..."
- "The proposed model yields..."
- "The magnitude is compared with..."
- "This is a working hypothesis in the source text."

Avoid:
- "This proves dark energy is Casimir energy."
- "Vacuum polarizability is directly observed at zero field."
- "Every quantum field has exactly this value."
- "The cosmological constant problem is solved."

## A0. Finite intrinsic vacuum polarizability is a working hypothesis

Source support:
- Lines 63-67 propose transient particle/antiparticle fluctuations as dipoles and motivate intrinsic polarizability density.
- Lines 80-83 explicitly say the possibility of observing intrinsic zero-field vacuum polarization is contentious, and that the finite vacuum polarizability density is used as a working hypothesis.

Animation placement:
- Episode 1, before the first dipole field becomes a measurable density.

On-screen caveat:
- "Working hypothesis: a finite zero-field polarizability density."

Visual treatment:
- Show the zero-point dipoles as translucent/flickering, not as literal permanent particles.
- Use opacity and labels to distinguish virtual fluctuations from observed matter.

## A1. Polarizability density-density tensor is reduced to static homogeneous density

Source support:
- Lines 69-72 define the PDDT and explain time homogeneity / zero-frequency limiting.
- Lines 101-104 state the internal polarization dynamics are not known in detail and the paper uses coarse-grained models respecting homogeneity and isotropy.
- Line 103 introduces static (`u=0`) full-potential (`lambda=1`) approximation in the retarded Casimir regime.

Animation placement:
- Episode 2, after Eq. (1) is introduced.

On-screen caveat:
- "Coarse-graining: unknown full response -> homogeneous/isotropic static model."

Visual treatment:
- Start with a complex 4D response web, then blur/average it into a smooth field.
- Do not pretend the full tensor dynamics are computed exactly in later scenes.

## A2. Effective electron/positron radius is the Thomson scattering length

Source support:
- Lines 99 and 114-116 discuss elementary particles as structureless but acquiring effective orbital size when probed, and choose `R_Th = alpha_fsc^2 a_0` for low-frequency elastic electron-photon interaction relevant to vdW/Casimir phenomena.

Animation placement:
- Episode 3, when Eq. (2) introduces `R_{e^-/e^+}`.

On-screen caveat:
- "Effective size under this low-frequency elastic probe: `R_Th = alpha_fsc^2 a_0`."

Visual treatment:
- Show a point electron acquiring a probe-dependent translucent radius, not a literal hard ball.

## A3. Electron/positron fluctuations are modeled as transient polarizable dipoles

Source support:
- Lines 63-65 and 108-116.

Animation placement:
- Episode 1 and Episode 3.

On-screen caveat:
- "Model: `e^-/e^+` fluctuation -> transient polarizable dipole."

Visual treatment:
- Use short-lived dipole flashes and ellipsoids with fade-in/fade-out.
- Avoid showing long-lived bound positronium unless explicitly labeled as an analogy.

## A4. Eq. (3) uses a second-order pairwise Casimir-Polder approximation

Source support:
- Lines 118-123: pairwise second-order approximation to Eq. (1).
- Lines 200-211: discusses applicability of the fully retarded Casimir-Polder energy and the retarded-regime validity condition.

Animation placement:
- Episode 4.

On-screen caveat:
- "Approximation: second-order pairwise Casimir-Polder interaction."

Visual treatment:
- Place Eq. (1) as a ghost in the background while Eq. (3) is introduced as a simplified path.
- Show the approximation gate: exact response -> two-pair interaction.

## A5. Dipole approximation and possible multipoles

Source support:
- Lines 213-216: equations employ dipole approximation; coarse-grained PDDT could make multipoles non-negligible, but octupolar contribution is estimated to be suppressed by `alpha_fsc^6`.

Animation placement:
- Episode 4 or caveats episode.

On-screen caveat:
- "Dipole approximation; higher multipoles argued to be tiny here."

Visual treatment:
- Show faint higher multipole shapes fading by a factor labeled `alpha_fsc^6`.

## A6. Many-body geometry is approximated by an effective lattice sum

Source support:
- Lines 136-151: field calculation requires summing pairwise potential over many-body geometries and approximates limiting behaviors with bcc/fcc lattice sums.

Animation placement:
- Episode 5.

On-screen caveat:
- "Geometry compressed into `N_eff`; bcc/fcc are bounding estimates."

Visual treatment:
- Side-by-side bcc/fcc ghost lattices, not a claim that the vacuum literally crystallizes.
- Label them as "arrangement models" or "weighted geometry estimates."

## A7. Spherical shell model replaces lattice uncertainty

Source support:
- Lines 154-165: uncertainty in `N_eff` can be avoided by deriving SIE density based on collective fluctuations of concentric spherical field shells, using homogeneity and isotropy.

Animation placement:
- Episode 6.

On-screen caveat:
- "Alternative coarse-graining: isotropic shell model."

Visual treatment:
- Transition from discrete lattice points dissolving into smooth concentric shells.
- Make this feel like a modeling choice, not an experimental image.

## A8. Final value is compared to cosmological constant estimates by magnitude

Source support:
- Lines 148-151 and 185 quote the numerical agreement with estimates of vacuum energy density from the cosmological constant.
- Line 150 explicitly says "barring the sign to be discussed below."
- Lines 192-198 discuss negative SIE sign, equation of state, pressure, and effective sign for matter relative to vacuum polarization.

Animation placement:
- Episode 7.

On-screen caveat:
- "Magnitude comparison; sign and interpretation require care."

Visual treatment:
- Use a bracket/interval chart: Planck estimate, shell-model value, Hubble estimate.
- Do not use a celebratory "solved" graphic.

## A9. `w=-1` comes from the model's volume scaling

Source support:
- Lines 192-197: `w=P/Ebar_SIE=-1`, `P=-dE/dV`, and `E_SIE proportional Ebar_SIE V`.

Animation placement:
- Episode 7.

On-screen caveat:
- "Model equation of state: constant density under volume expansion."

Visual treatment:
- Expanding off-white transparent box with density texture staying constant.
- Equation card remains front-facing while arrows indicate pressure.

## A10. Extension to other fields is speculative / requires additional propagators

Source support:
- Lines 220-230 discuss heavier charged lepton fields and then state that fields beyond charged leptons require propagators other than electromagnetic and high-energy FSC changes.
- Lines 230-236 frame scale-invariant SIE for arbitrary fields as an elegant possible outcome.

Animation placement:
- Episode 8, caveats / outlook.

On-screen caveat:
- "Beyond charged leptons: additional propagators and high-energy behavior required."

Visual treatment:
- Keep other fields as dim silhouettes beyond the electron/positron track.

## Caveat checklist per episode

Episode 0:
- State the whole animation is a model walkthrough.

Episode 1:
- A0, A3.

Episode 2:
- A1.

Episode 3:
- A2, A3.

Episode 4:
- A4, A5.

Episode 5:
- A6.

Episode 6:
- A7.

Episode 7:
- A8, A9.

Episode 8:
- A10 plus recap of the strongest assumptions.
