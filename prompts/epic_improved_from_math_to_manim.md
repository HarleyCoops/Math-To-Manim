# Epic-improved prompt pack from original Math-To-Manim examples

These prompts are based on concrete subjects/prompts in the original repo at `/mnt/c/Users/chris/Math-To-Manim`, but they are intentionally not "similar output" prompts. They ask M2M2 to produce upgraded, more cinematic, more explanatory, more polished scenes.

## Source examples copied as subject anchors

1. Fourier Epicycles
   Source: `/mnt/c/Users/chris/Math-To-Manim/examples/mathematics/fourier/fourier_epicycles.py`
   Original idea: rotating complex exponentials / circles stack into epicycles that trace a curve; scenes include circular motion, sine projection, complex rotation, stacking epicycles, and drawing a shape.

2. Lorenz Attractor
   Source: `/mnt/c/Users/chris/Math-To-Manim/examples/lorenz_attractor_3d.py` and `/mnt/c/Users/chris/Math-To-Manim/docs/EXAMPLES.md`
   Original idea: integrate the Lorenz system with sigma=10, rho=28, beta=8/3, draw the butterfly strange attractor with color-changing 3D trails and camera rotation.

3. Volatility / Star-Field Finance
   Source: `/mnt/c/Users/chris/Math-To-Manim/examples/finance/optionskew.py`
   Original idea: star field -> standard deviation -> Brownian paths -> heat equation -> Black-Scholes PDE -> implied volatility surface / skew.

4. QED from Spacetime to Photon Exchange
   Source: `/mnt/c/Users/chris/Math-To-Manim/examples/physics/quantum/SpacetimeQEDScene.py`
   Original idea: cosmic starfield, Minkowski frame, light cone, metric equation, E/B waves, Maxwell equations, QED Lagrangian, Feynman diagram / photon exchange.

5. Topology / Euler Polyhedron Formula
   Source: `/mnt/c/Users/chris/Math-To-Manim/examples/mathematics/topology/euler_polyhedron_formula.py`
   Original idea: count vertices, edges, and faces of tetrahedron/cube/dodecahedron to reveal V - E + F = 2 as a topological invariant.

---

# Recommended master prompt: epic improved Volatility Star-Chart Statistics

Create a 75-90 second cinematic Manim animation titled:

"Star-Chart Statistics: From Random Motion to the Volatility Surface"

Goal:
Make an epically improved version of the old Math-To-Manim volatility/options-skew scene. Do not merely recreate it. Turn it into a premium 3Blue1Brown-meets-IMAX explainer where the visuals feel like a cosmic navigation chart that gradually becomes rigorous financial mathematics.

Narrative beats:

1. Cold open: a dark cinematic star field
   - Begin in deep space with hundreds of tiny stars arranged like a star chart.
   - Draw faint constellation lines between selected points.
   - Label the opening idea: "statistics is geometry for uncertainty".
   - The title should appear only after the chart is visually established, not before.

2. Stars become data
   - Transform the star field into a 3D point cloud around a glowing mean point mu.
   - Show deviations as thin radial vectors from mu to sample points.
   - Write the standard deviation formula:
     sigma = sqrt(1/N sum_i (x_i - mu)^2)
   - Animate the variance as a translucent sphere whose radius pulses with sigma.

3. Data becomes Brownian motion
   - Collapse the point cloud into multiple animated Brownian sample paths.
   - The paths should look like luminous market trajectories, not random scribbles.
   - Add the geometric Brownian motion equation:
     S_t = S_0 exp((r - 1/2 sigma^2)t + sigma W_t)
   - Visually distinguish drift, volatility, and noise with color-coded overlays.

4. Brownian paths become a heat/diffusion surface
   - Morph the path bundle into a glowing diffusion surface.
   - Show the heat-equation intuition:
     partial f / partial t = 1/2 sigma^2 partial^2 f / partial x^2
   - Make probability density visibly spread over time.
   - Include a brief split-screen moment: left side sample paths, right side smooth density surface.

5. Diffusion becomes Black-Scholes
   - Reveal 3D axes for stock price S, time T, and option value C.
   - Write the Black-Scholes PDE:
     partial C/partial t + 1/2 sigma^2 S^2 partial^2 C/partial S^2 + rS partial C/partial S - rC = 0
   - Show the PDE terms as forces shaping the surface: diffusion bends it, drift tilts it, discounting dims it.

6. Finale: implied volatility surface / skew
   - Transform the option value surface into a color-coded implied volatility surface sigma(K,T).
   - Axes: strike K, maturity T, implied volatility sigma.
   - The surface should have an obvious volatility smile/skew, with color gradient blue -> cyan -> gold -> red.
   - Use a cinematic orbit around the surface and label three points: at-the-money, downside skew, long maturity term structure.
   - End by pulling back until the volatility surface resembles the opening star chart, closing the loop.

Visual style:
- Premium cinematic math explainer.
- Dark background, neon constellations, tasteful glow, high contrast labels.
- Smooth camera moves, no jitter, no clutter.
- Use 3D surfaces, translucent meshes, particle trails, and color-coded equations.
- The scene should feel much more polished than the original: fewer static equations, more transformations where each object becomes the next concept.

Math/explanation requirements:
- Make the conceptual chain explicit: data scatter -> sigma -> Brownian motion -> diffusion PDE -> Black-Scholes -> implied volatility surface.
- Keep equations readable and not on screen all at once.
- Use callout labels that teach what each equation term does.
- Include a final one-sentence takeaway: "Volatility is uncertainty made geometric."

Technical Manim constraints:
- Use `ThreeDScene` for the main scene.
- Use deterministic random seeds so the animation is reproducible.
- If using camera changes in Manim CE, use `self.move_camera(...)`, `self.set_camera_orientation(...)`, and ambient camera rotation; do not call `.animate` on `self.camera`.
- Keep generated code self-contained with helper functions for star fields, Brownian paths, diffusion surface, and volatility surface.
- Prefer stable Manim primitives: Dot3D, Line3D, VMobject, VGroup, Surface, ThreeDAxes, MathTex, Text, always_redraw only where necessary.
- Include enough comments in the generated scene to make the conceptual structure obvious.

Expected output:
A single polished Manim scene that feels like a major upgrade over the old `optionskew.py`: same subject lineage, but more cinematic, better staged, more mathematically legible, and much more visually memorable.

---

# Alternate epic prompt: Lorenz Attractor Symphony 2.0

Create a 75-90 second cinematic 3D Manim animation titled:

"Chaos Has a Shape: The Lorenz Attractor Symphony"

Make an epically improved version of the original Lorenz attractor scene. Start with two nearly identical glowing particles launched from almost the same point. Integrate and visualize the Lorenz system with sigma=10, rho=28, beta=8/3. Show their paths separating slowly at first, then dramatically, while a translucent butterfly-shaped attractor emerges from thousands of trajectory points. Use velocity-based color mapping from cool cyan to hot red, multiple ghost trajectories, and camera fly-throughs. Display the Lorenz equations cleanly, then introduce the idea of a positive Lyapunov exponent as "nearby futures separate exponentially." End with a top-down view where the attractor looks like a living butterfly, with the takeaway: "deterministic does not mean predictable."

Technical constraints: use `ThreeDScene`, deterministic seed, precomputed points, stable VMobject path segments, readable fixed-in-frame text, and `move_camera` instead of `self.camera.animate`.

---

# Alternate epic prompt: Fourier Epicycles Deluxe

Create a 75-90 second cinematic Manim animation titled:

"Drawing with Frequencies: Fourier Epicycles"

Make an epically improved version of the old Fourier epicycles animation. Begin with a single rotating complex number e^{it}. Project it into a sine wave, then split it into multiple rotating vectors with different amplitudes and frequencies. Show the equation z(t)=sum c_n e^{int}, with each term color-matched to one epicycle. The circles should chain tip-to-tail and trace an elegant glowing curve. Improve the original by adding a frequency spectrum panel, visible coefficient bars, and a final reveal where many small circles reconstruct a recognizable curve. The core teaching moment: a complicated shape is a choreography of simple rotations.

Visual style: clean dark background or elegant off-white, neon accent colors, smooth transformations, readable labels, no clutter. Use stable Manim primitives and keep all math labels fixed in frame.

---

# Alternate epic prompt: QED Spacetime, but safer and more cinematic

Create a 90 second cinematic 3D Manim animation titled:

"QED: Light, Fields, and Photon Exchange"

Make an epically improved version of the old SpacetimeQEDScene. Start in a dense cosmic starfield, reveal a Minkowski coordinate frame and glowing light cone, then write ds^2 = -c^2dt^2 + dx^2 + dy^2 + dz^2 with color-coded terms. Transition into perpendicular electric and magnetic waves propagating through space. Collapse classical Maxwell equations into the tensor form partial_mu F^{mu nu}=mu_0 J^nu. Then reveal the QED Lagrangian, highlighting the spinor field, gamma matrices, covariant derivative, and field strength tensor. End with an electron-electron scattering Feynman diagram where a wavy photon line carries the interaction.

Important technical constraint: in Manim CE, never call `.animate` on `self.camera` or `self.camera.frame`. Use `self.move_camera(...)`, `self.set_camera_orientation(...)`, and `begin_ambient_camera_rotation(...)` only.
