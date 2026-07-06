# Beat Sheet: Casimir SIE Paper Explainer

Production goal: a sequence of readable, cinematic, off-white 3D Math-To-Manim/Manim episodes that teach the derivation in PRL 130, 041601. Every equation gets a front-facing formula card before becoming geometry.

## Global visual grammar

- Background: warm off-white / bone.
- Formula cards: large, fixed-in-frame, ink text, high contrast, rounded rectangle, subtle shadow.
- 3D geometry: translucent glass-like fields, muted saturated accents, thin dark outlines.
- Motion rule: the camera may orbit geometry only after the equation has been readable from the viewer's perspective.
- Caveat rule: every approximation gets a small gold "MODEL STEP" or muted red "CAVEAT" tag.

## Episode 0: Argument Map — From Vacuum Dipoles to Lambda-Scale Energy Density

Duration target: 60-90 seconds.

Learning objective:
- Give the viewer a map of the entire paper before details begin.

Beats:
1. Title card on bone background:
   "Casimir Self-Interaction Energy Density of Quantum Electrodynamic Fields"
2. A quiet empty 3D volume appears; tiny dipole flashes appear and disappear.
3. The central chain builds as spatial nodes:
   `vacuum fluctuations -> polarizability density -> Casimir SIE -> lattice/shell models -> Lambda-scale density`.
4. The final number appears only as destination, not proof:
   `|Ebar_SIE| = 2.07 x 10^-23 Ha/Bohr^3`.
5. Caveat card:
   "We are visualizing a proposed model and its assumptions."
6. Transition: zoom through the first node, "transient dipoles."

Key visuals:
- 3D node graph suspended above an off-white plane.
- One formula card with the final Eq. (11) only briefly visible, blurred, then marked "destination."

Equations:
- No full derivation; show final Eq. (11) as preview only.

Acceptance criteria:
- Viewer understands the roadmap.
- Not overclaimed.
- Text readable in contact sheet frames.

## Episode 1: Vacuum Fluctuations as Polarizable Dipoles

Duration target: 2-3 minutes.

Learning objective:
- Explain why the paper begins by treating QED field fluctuations as transient dipoles with finite polarizability density.

Beats:
1. Empty volume on bone background; faint grid marks space.
2. Particle-antiparticle pairs appear as red/blue points, separating slightly, connected by dipole arrows.
3. Pairs fade quickly to show transience.
4. A formula/definition card introduces the PDDT idea in words:
   `alpha_F(r,r',t,t') = delta P(r,t) / delta E(r',t')`.
5. The 4D/time-dependent tensor web averages into a smooth homogeneous polarizability density.
6. Caveat card from source lines 80-83:
   "Finite zero-field polarizability density is a working hypothesis."
7. Visual payoff: many transient dipoles blur into a translucent field texture labeled `alpha_F(r)`.

Equations/labels:
- PDDT definition from source text, not numbered.
- `alpha_F(r)` as static density.

Acceptance criteria:
- Virtual/transient nature clear.
- Working-hypothesis caveat visible.
- No permanent particles implied.

## Episode 2: Eq. (1) — The Formal Energy Density Machine

Duration target: 3-4 minutes.

Learning objective:
- Turn the ACFDT expression into a visual machine: integrate over frequency, coupling, and volume; contract response with propagator.

Beats:
1. Large Eq. (1) formula card, held long enough to read.
2. Highlight `u`: formula zooms into frequency axis, then returns.
3. Highlight `lambda`: slider turns interactions on from bare to full.
4. Highlight `r,r'`: two points scan the vacuum volume.
5. Highlight `alpha_lambda - alpha_0`: response cloud appears as difference between interacting and bare fluctuation fields.
6. Highlight `T`: retarded dipole bridge/light cone connects the two points.
7. Highlight `Tr`: tensor box collapses into scalar energy density.
8. Caveat transition: exact machine is too complex; we will build coarse-grained models.

Equations:
- Eq. (1) `eqExact`.

Acceptance criteria:
- Every symbol receives a visual mapping.
- Viewer sees Eq. (1) as the source of later approximations.

## Episode 3: Eq. (2) — Polarizability Scaling of an e-/e+ Pair

Duration target: 2-3 minutes.

Learning objective:
- Explain how the paper assigns a polarizability to an electron/positron fluctuation using a radius scaling law.

Beats:
1. Formula card Eq. (2), held.
2. Isolate `R_{e^-/e^+}`; a point pair acquires an effective translucent radius.
3. Label the chosen radius: `R_Th = alpha_fsc^2 a_0`.
4. Show `R^3` as volume.
5. Show `(alpha_fsc^{1/3} R/a_0)^4` as four nested photon-dressing shells.
6. Show `2/3`: two polarizable charges, averaged over three directions.
7. Final geometry: one polarizable dipole ellipsoid with all factors annotated.

Equations:
- Eq. (2).
- Radius relation `R_Th = alpha_fsc^2 a_0`.

Caveat:
- Effective probe-dependent radius, not literal particle size.

## Episode 4: Eqs. (3)-(5) — Two-Pair Casimir Energy

Duration target: 3-4 minutes.

Learning objective:
- Show how pair polarizability becomes a pairwise Casimir self-interaction energy density.

Beats:
1. Eq. (3) formula card.
2. Two dipole ellipsoids appear; separation label `2R`.
3. The `R^{-7}` law is visualized by rapidly fading connection strength as distance grows.
4. Eq. (2)'s `alpha` symbol substitutes into Eq. (3).
5. Morph Eq. (3) into Eq. (4); cancellation leaves `R^4`.
6. Insert `R_Th = alpha_fsc^2 a_0`; morph Eq. (4) into Eq. (5).
7. Constants compress into `E_h/a_0^3`.

Equations:
- Eq. (3), Eq. (4), Eq. (5).

Caveat:
- Pairwise second-order Casimir-Polder approximation; dipole approximation.

## Episode 5: Eqs. (6)-(7) — Lattice Sum of Many Pair Interactions

Duration target: 3-4 minutes.

Learning objective:
- Show how a many-body field estimate is approximated by multiplying the pair energy by a weighted geometry count.

Beats:
1. Eq. (6) formula card.
2. A single pairwise tile duplicates into many arrangements.
3. Eq. (7) formula card.
4. Build bcc and fcc point lattices side-by-side.
5. From the origin, draw weighted links; opacity scales as `|R_j|^{-7}`.
6. Counters land on `N_eff^bcc = 11.05` and `N_eff^fcc = 13.36`.
7. Output interval appears: `{1.85, 2.24} x 10^-23 Ha/Bohr^3`.

Equations:
- Eq. (6), Eq. (7).

Caveat:
- Lattice is a weighted arrangement model, not a literal crystalline vacuum.

## Episode 6: Eqs. (8)-(11) — Spherical Shell Derivation

Duration target: 4-5 minutes.

Learning objective:
- Replace the lattice uncertainty with a homogeneous/isotropic shell model and reach the final power law.

Beats:
1. Lattice dissolves into a sphere.
2. Eq. (8) formula card; shell radius `r` appears.
3. Shell area `4 pi r^2`, dressing factor, and `r^3` volume appear one by one.
4. Eq. (9) formula card; shells sweep from `0` to `r_f` into an accumulator.
5. Marker: `r_f = alpha_fsc^{5/3} a_0`.
6. Eq. (10) appears as the integral's evaluated form; shell stack collapses to `r_f^6`.
7. Substitute `r_f`; exponents combine into Eq. (11).
8. Final formula card held.

Equations:
- Eq. (8), Eq. (9), Eq. (10), Eq. (11).

Caveat:
- Spherical shell model is an alternative coarse-graining.

## Episode 7: Dark-Energy-Like Equation of State and Lambda Comparison

Duration target: 2-3 minutes.

Learning objective:
- Explain the `w=-1` claim and the numerical comparison without overclaiming.

Beats:
1. Formula card: `w = P/Ebar_SIE = -1`, `P=-dE/dV`, `E_SIE proportional Ebar_SIE V`.
2. A transparent volume expands; energy density texture remains constant.
3. Pressure arrows and density label explain the sign relation carefully.
4. Numeric comparison chart:
   - Planck: `1.84 x 10^-23`
   - Shell model: `2.07 x 10^-23`
   - Hubble: `2.20 x 10^-23`
5. Caveat: "Magnitude comparison; sign and interpretation require care."

Equations:
- Non-numbered equation of state.
- Numeric value from Eq. (11).

## Episode 8: Model Audit and Final Mental Model

Duration target: 1-2 minutes.

Learning objective:
- Summarize what was shown and which assumptions carry the result.

Beats:
1. Reassemble the full argument chain as a 3D path.
2. Each approximation gate lights up with a caveat label.
3. The final formula sits beside the visual model: fluctuating dipoles, pair interactions, shells, comparison chart.
4. Final takeaway:
   "The paper proposes a polarizability-density route from QED fluctuations to a finite Casimir self-interaction energy density with dark-energy-like scaling."
5. End card lists source DOI and arXiv ID.

Acceptance criteria:
- Viewer leaves with both the idea and the caveats.
