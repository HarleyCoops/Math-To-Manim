# The third rhythm · TOI-4342

A reverse reasoning story for one star: two confirmed planets, then an 18.908-day transiting candidate found by [eumemic/exoplanets](https://github.com/eumemic/exoplanets). The explorable version keeps every teaching object in a 3D stage.

[Explore the Three.js scene](interactive.html) · [Read the reverse prerequisite tree and storyboard](STORY.md) · [Inspect the source snapshot](sources/provenance.json)

[Watch the 94-second Manim draft](../assets/toi4342-third-rhythm.mp4) · [Selected-moment GIF](../assets/toi4342-third-rhythm.gif) · [Contact sheet](../assets/toi4342-third-rhythm-contact-sheet.png) · [Saved scene](../../../examples/astra/toi4342_third_rhythm.py)

The candidate is unresolved. The saved Gaia-constrained TRICERATOPS result has mean FPP 0.11135 across ten runs; this exceeds the 0.015 statistical-validation threshold. The separate 47.5-day RV candidate in the literature is a different signal.

## Explore locally

From the repository root:

```powershell
python -m http.server 8876 --bind 127.0.0.1
```

Open `http://127.0.0.1:8876/docs/showcase/toi4342-third-signal/interactive.html`. Drag to rotate, scroll to zoom, and use the scene selector. Motion starts paused. The observer view uses orthographic projection so the transit silhouette preserves the fitted radius ratio.

The seven scenes walk backward to prerequisites, then forward through orbital rhythms, blocked light, a celestial viewing-direction belt, phase folding, actual sector-depth summaries, and the remaining candidate. The orbit curves are loops (S¹), the star's surface is a sphere (S²), and the viewing belt is an annulus on the direction sphere. These topology labels describe the teaching geometry; they do not validate the candidate.

The standalone page uses pinned Three.js 0.180.0 modules from jsDelivr. Rebuild it after editing `interactive-scene.html`:

```powershell
python scripts/build_toi4342_showcase.py
```

## Film production

The completed draft is **94 seconds at 1280 × 720, 30 fps**, with 2,820 frames and a successful full-file FFmpeg decode. The [production record](production.json) binds the published movie and saved source to their SHA-256 hashes.

GPT-6 Astra authored the brief, mathematics, storyboard, scene and two small production refinements through the official Codex SDK with cached ChatGPT login. The original chain ran with real TypeSafe Jev in advisory mode. Its actual assessments are retained in [production/](production/), including the original frame audit's clarity concerns.

The final local edit corrects caption encoding and removes evidence/concept markers that looked like additional planets in the ending. It combines the completed first 86 seconds with a locally rendered eight-second ending, a short editorial dissolve and a caption layer generated from the source's Manim overlay helper. Every colored stage pixel at the caption boundary was preserved. The final revision is labeled **not_reviewed**, without further Astra or Jev frame review; no Jev approval is claimed.

This is a first film draft. The original audit found small masking/phase objects, weak observer visibility and unclear associations in the prerequisite constellation. The labeled interactive scenes give these ideas more room to explore. Sampled frames and a successful decode do not certify every continuous occlusion or mathematical inference.

The saved-scene command uses the existing credential-clean local renderer, creates a fresh run manifest, and makes zero model or API calls:

```powershell
python scripts/render_toi4342.py -q m
```

Local renders receive `not_reviewed` status and preserve the original production reviews. Static source checks do not provide an OS or container sandbox.

## Data and assumptions

The source folder snapshots the candidate files at commit `ec8311b19a61092ad5eae3d34e947b14485d363e`, inspected October 12, 2026. [Tey et al. (2023)](https://arxiv.org/html/2301.01370v1) supplies the rounded host mass/radius and confirmed-planet periods.

- The model-derived circular semimajor axes are 0.052517, 0.081409, and 0.119075 AU.
- The overview preserves those distance ratios and the measured period ratios. Body sizes, orbital phases, mutual orientations, circularity, photospheric patterns, and photons are illustrative.
- The transit closeup uses fitted Rp/Rstar 0.0337894 and impact parameter 0.746895. The uniform-disk blocked-area approximation is 1141.7 ppm; actual light curves can include limb darkening and dilution.
- The public folder contains summary evidence rather than raw TESS light-curve samples. The phase cylinder is labeled synthetic, with enlarged transit widths. Masking removes samples in known transit windows; it does not subtract planet objects.
- The eight sector estimates and their reported errors are actual repository values. Sector spacing is categorical, and eight sectors are distinguished from nine fitted transit events.

Source data attribution and the repository's MIT license are retained in [sources/LICENSE-exoplanets.txt](sources/LICENSE-exoplanets.txt).
