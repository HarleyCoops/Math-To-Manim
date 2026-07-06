# Camera Grammar for the PRL 130, 041601 Manim Production

This file defines reusable visual/camera patterns for every episode. It exists to prevent the common failure mode where equations are technically present but unreadable or detached from the geometry.

## Rule 1: Formula card first

Every critical equation follows this sequence:

1. Full-screen or large center formula card.
2. Hold for reading.
3. Highlight one symbol group.
4. Zoom into the symbol group.
5. The symbol transforms into geometry.
6. Camera pulls back to show the geometry in context.
7. Return to formula card or keep a small pinned copy.

Never begin with a tilted 3D equation floating in space.

## Rule 2: Geometry earns the algebra

Use geometry to make the next algebraic transformation feel inevitable:

- `R^3` appears as volume before the viewer sees it as a factor.
- `R^{-7}` appears as rapidly fading connection strength before the denominator is emphasized.
- `sum_j` appears as many dim links accumulating into a counter.
- `int_0^{r_f}` appears as a shell sweep before it collapses into the evaluated expression.

## Rule 3: Approximation gates

When the derivation changes from exact formal expression to model approximation, the camera passes through an explicit gate.

Gate design:
- Small gold label: `MODEL STEP`.
- Small red label if contentious: `CAVEAT`.
- Before gate: exact/dense/complex visual.
- After gate: simplified/coarse-grained visual.

Examples:
- Eq. (1) -> homogeneous static model.
- Full field response -> pairwise Casimir-Polder form.
- Many-body arrangements -> lattice sum.
- Lattice uncertainty -> spherical shells.

## Rule 4: Off-white high-contrast readability

Background:
- `#F4EFE3` or `#F7F1E6`.

Formula card:
- Card fill: `#FFF8EA`.
- Border: `#C8BFAE`.
- Main text: `#1F2933`.
- Symbol highlight colors:
  - `alpha`: teal `#38A3A5`
  - radius / distance: deep blue `#22577A`
  - energy: muted red `#C8553D`
  - integration/sum: warm gold `#D9A441`
  - caveat/model tag: violet/gold depending on severity.

## Rule 5: 3D camera moves only after reading holds

Each scene's equation card is fixed front-facing while read.
Only after the formula has been held may the camera move into 3D geometry.

Recommended timing:
- New equation card write/fade: 1.2-1.8 s.
- Hold after full equation: 1.5-2.5 s.
- Highlight symbol group: 0.6-1.0 s.
- Transform symbol to geometry: 1.5-2.5 s.
- Geometry orbit: 4-8 s only if no formula is being introduced.
- Summary hold: 1.5-3.0 s.

## Pattern A: Formula -> 3D symbol object

Use for Eq. (2), Eq. (3), Eq. (8).

Steps:
1. Display formula card.
2. Surround target symbol with a colored rectangle.
3. Duplicate symbol as a floating label.
4. Move duplicate to 3D stage.
5. Fade in corresponding geometry under it.

Examples:
- `R_{e^-/e^+}` -> effective translucent radius sphere.
- `alpha_{e^-/e^+}` -> polarizability ellipsoid.
- `bar{alpha}(r)` -> glowing shell density.

## Pattern B: Integral -> sweep

Use for Eq. (1) and Eq. (9).

Steps:
1. Highlight integral bounds.
2. Create a scanning parameter marker.
3. Sweep through geometry while a progress trace accumulates.
4. Collapse the sweep trace into the resulting scalar or compact expression.

Examples:
- `int_V int_V dr dr'` -> two scan points moving through the volume.
- `int_0^{r_f}` -> shell expansion from center to cutoff radius.

## Pattern C: Sum -> weighted network

Use for Eq. (7).

Steps:
1. Highlight `sum_{R_j != 0}`.
2. Generate points around an origin.
3. Draw links from origin to points.
4. Link opacity/thickness follows `|R_j|^{-7}`.
5. Numeric counter accumulates toward `N_eff`.

## Pattern D: Power-law cancellation

Use for Eqs. (3)-(5) and Eq. (11).

Steps:
1. Highlight numerator powers in one color and denominator powers in another.
2. Move matching powers toward each other.
3. Fade canceled powers into ghost marks.
4. Surviving power moves into final formula.

Examples:
- Eq. (3) + Eq. (2) -> Eq. (4): radius powers condense to `R^4`.
- Eq. (10) + `r_f = alpha_fsc^{5/3}a_0` -> Eq. (11): exponent cascade becomes `alpha_fsc^{31/3}` in Hartree/Bohr units.

## Pattern E: Comparison chart

Use for Episode 7.

Steps:
1. Build horizontal log/linear local scale with three ticks.
2. Place Planck estimate, model value, Hubble estimate.
3. Use bracket label: "same quoted interval scale".
4. Add caveat label: "magnitude comparison, not proof."

## Production checks

For every rendered episode contact sheet, manually verify:

- Formula cards are readable in still frames.
- No important text is tilted or clipped.
- Caveat labels appear before or during each approximation.
- Off-white background is actually visible.
- Geometry reinforces the equation rather than distracting from it.
