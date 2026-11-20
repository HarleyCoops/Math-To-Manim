# Launch Posts: Chaining Theta Lifts to the Critical Line (Nov 20, 2026)

> Attach the native 720p30 video (`riemann-hypothesis-2026.mp4`, 52.4 s, 2.83 MB) directly to X and Reddit posts so it auto-plays in the feed.

---

## 1. X / Twitter Post (Attach `riemann-hypothesis-2026.mp4`)

Two claimed proofs of the Generalized Riemann Hypothesis dropped on the same day (Nov 20, 2026):
• Levent Alpöge & Claude: 175,000+ Lean 4 files chaining ~√X automorphic theta lifts
• Alessandro Masullo (Stanford): 12-year, ~940-page human manuscript

I reimagined Math-To-Manim into a single-command **Gemini 4 Neon** CLI (`math-to-manim-neon`) and rendered this 52-second 3D Manim explainer — zero repairs, all formulas numerically checked via AST tools.

*(Both proofs are newly announced and awaiting independent verification.)*

Playable gallery + open-source code + zero-install Colab in the reply ↓

**Reply tweet:**
Repo: https://github.com/HarleyCoops/Math-To-Manim
Playable multi-model gallery (Gemini 4 Neon, Claude Fable 5.2, Opus 5.5, GPT-6 Astra): https://harleycoops.github.io/Math-To-Manim/
Try in Colab (no install): https://colab.research.google.com/github/HarleyCoops/Math-To-Manim/blob/main/notebooks/math_to_manim_neon_colab.ipynb

---

## 2. Hacker News (`Show HN`)

**Title:** `Show HN: Math-To-Manim – Turn frontier math into 3D Manim films in one Gemini 4 Neon CLI call`
**URL:** `https://github.com/HarleyCoops/Math-To-Manim`

**Top comment:**
Hi HN — I've been building Math-To-Manim as an open-source multi-model lab where each frontier model gets its own isolated silo (`tests/test_silo_boundaries.py`) to turn hard mathematical topics into verified 3D Manim / Blender films.

Today, with two separate Generalized Riemann Hypothesis proof claims announced on the same day (Levent Alpöge & Claude's 175,000+ Lean 4 archive using chained theta lifts of length ~√X, and Alessandro Masullo's 12-year 940-page human manuscript), I reimagined our old 6-stage sequential pipeline into a single-call Gemini 4 Neon CLI (`math-to-manim-neon`):

- Unified planning + sandboxed NumPy/complex `verify_math` + AST/ThreeDScene `check_scene` + secret-scrubbed Manim render + FFmpeg contact sheet/GIF generation in one command.
- Rendered the 52.4s 720p30 film *Chaining Theta Lifts to the Critical Line* on the first try with 0 repairs (while explicitly noting both Nov 20 claims await independent peer and Lean-kernel verification).
- Added a zero-install Colab notebook and a playable gallery comparing Gemini 4 Neon, Gemini 4 Argon, Claude Fable 5.2, Claude Opus 5.5, and GPT-6 Astra.

Happy to answer questions on the silo architecture, Manim verification, or how different frontier models compare on 3D mathematical visualization!

---

## 3. Reddit (`r/3Blue1Brown` / `r/math`)

**Title:** `I built an open-source 3D Manim film explaining today's two Generalized Riemann Hypothesis proof announcements (Chaining Theta Lifts vs. 12-year human proof)`

**Body (with native video uploaded):**
With two major claimed proofs of GRH announced today (Nov 20, 2026) — Levent Alpöge & Claude's 4-page overview + 175,000+ Lean 4 files on chaining ~√X automorphic theta lifts to bypass Stepanov's missing integer derivative, and Stanford postdoc Alessandro Masullo's 12-year ~940-page manuscript — I ran my open-source `Math-To-Manim` pipeline (`math-to-manim-neon`) to visualize the core geometry in 52 seconds:

1. **Act I:** 3D surface of $\log(1 + |\zeta(\sigma + it)|)$ over the critical strip and the first five zero wells on $\operatorname{Re}(s) = 1/2$.
2. **Act II:** Why Stepanov's multiplicity method works over function fields $\mathbb{F}_q[t]$ (differentiation) vs. discrete prime-power spikes $\Lambda(n) = \log p$ over $\mathbb{Z}$.
3. **Act III:** Chaining $L \asymp \sqrt{X}$ automorphic theta lifts in 3D ($L=10$ for $X=100$).
4. **Act IV:** Side-by-side comparison of both announcements — clearly noting neither is yet peer-verified.

Full Manim source code (421 lines) + Colab notebook: https://github.com/HarleyCoops/Math-To-Manim
