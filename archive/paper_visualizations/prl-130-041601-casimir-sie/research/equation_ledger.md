# Equation Ledger: PRL 130, 041601 Casimir SIE Visualization

Source paper: Alexandre Tkatchenko and Dmitry V. Fedorov, "Casimir Self-Interaction Energy Density of Quantum Electrodynamic Fields," Phys. Rev. Lett. 130, 041601.

Primary provenance:
- Publisher PDF: `/mnt/c/Users/chris/Math-To-Manim/PhysRevLett.130.041601.pdf`
- Extracted PDF text: `research/pdf_text_pages.md`
- arXiv source archive: `latex/arxiv_source/source.tar.gz`
- arXiv source TeX: `latex/arxiv_source/Lambda_resubmission.tex`
- Raw extracted equation blocks: `latex/equations.tex`
- Manim-ready cleaned equations: `latex/display_equations.tex`

## Narrative spine

The paper's argument chain is:

1. Quantum electrodynamic fields have transient particle-antiparticle pair fluctuations.
2. Electrodynamic pair fluctuations can be modeled as short-lived dipoles with a finite polarizability density.
3. Casimir/vdW self-interaction energy density can be expressed through a polarizability-density response and a dipolar propagator.
4. For electron/positron fluctuations, a quantum scaling law links polarizability to an effective vdW/Thomson radius.
5. A two-pair Casimir-Polder approximation gives a pairwise self-interaction energy density.
6. Summing pairwise interactions through a bcc/fcc-like lattice gives a plausible range.
7. A spherical-shell model removes lattice-choice uncertainty and yields a compact fine-structure-constant power law.
8. The resulting magnitude lies between two quoted cosmological-constant estimates and the model has equation of state `w=-1`.

Important caveat for narration: the finite intrinsic zero-field polarizability density is explicitly a working hypothesis in the source. The visualization should label model assumptions, not imply experimental certainty.

---

## Eq. (1): Exact ACFDT/Casimir self-interaction expression

Source label: `eqExact`, arXiv source lines 91-95.

Clean display LaTeX:

```tex
\bar{E}_{\mathrm{SIE}}
= \frac{\hbar}{2\pi V}
\int_0^{\infty} du\int_0^1 d\lambda
\int_V\int_V d\mathbf{r}\,d\mathbf{r}'
\,\mathrm{Tr}\left\{\left[
\boldsymbol{\alpha}_{\lambda}(\mathbf{r},\mathbf{r}',iu)
-\boldsymbol{\alpha}_{0}(\mathbf{r},\mathbf{r}',iu)
\right]\mathbf{T}(\mathbf{r},\mathbf{r}',iu)\right\}
```

Plain meaning:
- `\bar{E}_{\mathrm{SIE}}` is the self-interaction energy density.
- The `u` integral sweeps imaginary frequency.
- The `\lambda` integral turns interactions on from bare (`0`) to full (`1`).
- The two spatial integrals sweep all source/response points in volume `V`.
- The trace contracts the polarizability-response difference with the dipolar propagator.

Visual mapping:
- Start with a translucent vacuum volume `V`.
- Two points `r` and `r'` pulse inside it.
- A frequency dial `u` rises vertically like a spectral axis.
- A coupling slider `\lambda: 0 -> 1` brightens the response field.
- `\boldsymbol{\alpha}_\lambda - \boldsymbol{\alpha}_0` becomes a changing polarizability cloud.
- `\mathbf{T}` becomes a retarded light-cone/dipole influence bridge.
- `Tr{...}` becomes a contraction frame that collapses the tensor geometry into one scalar density.

Caveat label:
- "Exact formal starting point; later scenes introduce coarse-grained approximations."

---

## Eq. (2): Electron/positron polarizability scaling law

Source label: `eqAlphae-e+`, arXiv source lines 109-112.

```tex
\alpha_{e^-/e^+}
= \frac{2}{3}
\left(\frac{\alpha_{\mathrm{fsc}}^{1/3} R_{e^-/e^+}}{a_0}\right)^4
R_{e^-/e^+}^{3}
```

Plain meaning:
- Models an `e^-/e^+` pair as a transient polarizable dipole.
- Radius `R_{e^-/e^+}` contributes as `R^3` volume times a four-dimensional fine-structure dressing factor.
- The source text sets `R_{e^-/e^+}` to the Thomson scattering length `R_Th = alpha_fsc^2 a_0`.

Visual mapping:
- Show an electron and positron connected by a glowing dipole axis.
- Inflate a translucent ellipsoid around them as `R_{e^-/e^+}` grows.
- Pull out `R^3` as volume, then add the fourth-power dressing as four nested spectral shells.
- The factor `2/3` appears as "two charges" times "one of three degenerate directions."

Caveat label:
- "Modeling step: pair fluctuations are coarse-grained as polarizable dipoles."

---

## Eq. (3): Pairwise second-order Casimir SIE density

Source label: `eqC2body`, arXiv source lines 120-123.

```tex
\bar{E}_{\mathrm{SIE}}^{(2)}
= -\frac{23\hbar c}{4\pi}
\frac{\alpha_{e^-/e^+}^{2}}
{(2R_{e^-/e^+})^7 V_{e^-/e^+}}
```

Plain meaning:
- A second-order pairwise Casimir-Polder style estimate between two pair fluctuations.
- The interaction falls as seventh power of separation.
- The negative sign encodes attractive Casimir/vdW energy in the typical geometry.

Visual mapping:
- Two dipole-pair ellipsoids separated by `2R`.
- A bridge between them fades as `distance^{-7}`; nearest distances bright, farther distances nearly invisible.
- The numerator `alpha^2` becomes two glowing polarizability ellipsoids multiplying.
- Divide by `V` to express density.

Caveat label:
- "Approximation: pairwise second-order Casimir-Polder form."

---

## Eq. (4): Substitute polarizability into pairwise SIE

Source label: `eqC2body_R4`, arXiv source lines 125-128.

```tex
\bar{E}_{\mathrm{SIE}}^{(2)}
= -\frac{23\hbar c}{3072\pi^2}
\left(\frac{\alpha_{\mathrm{fsc}}^{1/3}}{a_0}\right)^8
\left(R_{e^-/e^+}\right)^4
```

Plain meaning:
- Eq. (2) is inserted into Eq. (3).
- Powers combine: the interaction denominator cancels much of the `R` dependence, leaving `R^4`.

Visual mapping:
- Equation morph: two `\alpha` symbols open into Eq. (2), powers flow through a cancellation tunnel.
- `R^7` denominator visibly eats part of the polarizability geometry.
- The remaining radius cube/power stack condenses to `R^4`.

---

## Eq. (5): Substitute Thomson radius and Hartree units

Source label: `eqC2bodynum`, arXiv source lines 130-134.

```tex
\bar{E}_{\mathrm{SIE}}^{(2)}
= -\frac{23\alpha_{\mathrm{fsc}}^{29/3}}{3072\pi^2}
\frac{\hbar c\alpha_{\mathrm{fsc}}}{a_0^4}
= -\frac{23\alpha_{\mathrm{fsc}}^{29/3}E_h}{3072\pi^2 a_0^3}
```

Plain meaning:
- Uses `R_{e^-/e^+}=alpha_fsc^2 a_0` and `E_h = hbar c alpha_fsc a_0^{-1}`.
- Converts the result into atomic energy density units.

Visual mapping:
- The Thomson radius label drops onto `R_{e^-/e^+}`.
- A power counter accumulates fine-structure exponents.
- Constants compress into a small unit block: `E_h/a_0^3`.

---

## Eq. (6): Many-body field estimate through effective lattice count

Source label: `E_SIE_N_eff`, arXiv source lines 137-140.

```tex
\bar{E}_{\mathrm{SIE}}
= \bar{E}_{\mathrm{SIE}}^{(2)} N_{\mathrm{eff}}
```

Plain meaning:
- The pairwise contribution is multiplied by an effective weighted count of neighboring pair interactions.

Visual mapping:
- One two-pair tile duplicates into a lattice of possible arrangements.
- The pairwise energy tile multiplies by an accumulating `N_eff` counter.

Caveat label:
- "Estimate: many-body geometry is compressed into one weighted lattice sum."

---

## Eq. (7): Weighted bcc/fcc lattice sum

Source label: `lattice_sum`, arXiv source lines 143-147.

```tex
N_{\mathrm{eff}}
= \sum_{\mathbf{R}_j\ne\mathbf{0}}
\frac{(2R_{e^-/e^+})^7}{|\mathbf{R}_j|^7}
```

Plain meaning:
- Sum over all nonzero lattice vectors.
- The seventh-power denominator makes nearby neighbors dominate.
- Source gives limiting estimates: `N_eff^bcc = 11.05`, `N_eff^fcc = 13.36`.

Visual mapping:
- Split-screen bcc and fcc point clouds.
- Edges from origin to neighbors glow with opacity proportional to `|R_j|^{-7}`.
- Counters settle at 11.05 and 13.36.
- Output range: `|E_SIE| = {1.85, 2.24} x 10^{-23} Ha/Bohr^3`.

---

## Eq. (8): Radial polarizability density for spherical shell

Source label: `eqRadPol`, arXiv source lines 155-158.

```tex
\bar{\alpha}_{e^-/e^+}(r)
= \frac{4\pi r^2}{a_0^3}
\left(\frac{\alpha_{\mathrm{fsc}}^{1/3}r}{a_0}\right)^4 r^3
```

Plain meaning:
- Replaces discrete pair geometry with a collective isotropic shell model.
- Shell area `4 pi r^2`, fine-structure dressing, and radial volume factor combine into a radial polarizability density.

Visual mapping:
- A sphere centered at `r'=0` emits a thin shell at radius `r`.
- `4 pi r^2` appears as the shell surface area.
- The dressing factor appears as nested shell glows.
- `r^3` becomes a local volumetric blob riding on the shell.

Caveat label:
- "Alternate approximation: collective spherical shells replace uncertain lattice geometry."

---

## Eq. (9): Shell integral for SIE density

Source label: `E_SIE`, arXiv source lines 166-169.

```tex
\bar{E}_{\mathrm{SIE}}
= -\frac{3\hbar c}{8\pi a_0^3}
\int_0^{r_f}\frac{\bar{\alpha}_{e^-/e^+}(r)}{r^4}\,dr
```

Plain meaning:
- Sum shell contributions from the center to dressed Thomson length `r_f`.
- The denominator `r^4` weights the shell contribution.

Visual mapping:
- Concentric shells sweep outward from `0` to `r_f`.
- Each shell contributes a glowing ring into an integral accumulator.
- A vertical marker at `r_f = alpha_fsc^{5/3} a_0` stops the sweep.

---

## Eq. (10): Evaluated shell integral

Source label: `E_SIE_r_f`, arXiv source lines 171-176.

```tex
\bar{E}_{\mathrm{SIE}}
= -\frac{\hbar c}{4a_0^6}
\left(\frac{\alpha_{\mathrm{fsc}}^{1/3}}{a_0}\right)^4 r_f^6
```

Plain meaning:
- The integral collapses into a compact dependence on the cutoff radius `r_f^6`.

Visual mapping:
- The stack of shells compresses into a single `r_f^6` power block.
- The integral sign folds into the final expression.

---

## Eq. (11): Final fine-structure power law

Source label: `eqLambda`, arXiv source lines 178-183.

```tex
\bar{E}_{\mathrm{SIE}}
= -\frac{\hbar c\alpha_{\mathrm{fsc}}^{34/3}}{4a_0^4}
= -\frac{1}{4}\alpha_{\mathrm{fsc}}^{31/3}E_h a_0^{-3}
```

Plain meaning:
- Substitute `r_f = alpha_fsc^{5/3}a_0` into Eq. (10).
- Final density is expressed using a high power of the fine-structure constant.
- Source gives magnitude `2.07 x 10^-23 Ha/Bohr^3`.

Visual mapping:
- `r_f` opens into `alpha_fsc^{5/3}a_0`; exponents cascade and combine.
- A final formula card locks in place.
- Numeric comparison scale shows Planck/Hubble estimates bracketing the value.

Caveat label:
- "Result of the shell model under the paper's assumptions."

---

## Non-numbered endpoint: equation of state

Source lines 192-197.

```tex
w = \frac{P}{\bar{E}_{\mathrm{SIE}}} = -1,
\qquad P=-\frac{dE}{dV},
\qquad E_{\mathrm{SIE}}\propto \bar{E}_{\mathrm{SIE}}V
```

Plain meaning:
- The paper argues that because total SIE scales linearly with volume at fixed density, the pressure relation gives `w=-1`.

Visual mapping:
- An expanding transparent cube keeps the same internal energy-density texture.
- Pressure arrows point outward while the equation card explains `P=-dE/dV`.
- Use careful wording: "the model obeys the dark-energy-like equation of state" rather than "this proves dark energy."
