# Erdős 1038 README Hero Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Feature a verified 21.9-second Erdős 1038 GIF at the top of the root README with a verbose nontechnical explanation and a link to the full film.

**Architecture:** Join the accepted film’s 54–72 second proof sequence to its 75–78.9 second final tableau, encode a palette-optimized 720px GIF, inspect representative frames, and insert one self-contained hero block before the existing Traitor Axis feature.

**Tech Stack:** FFmpeg, ffprobe, Markdown, HTML.

## Global Constraints

- Preserve the star-history chart and every existing showcase entry.
- Use `docs/showcase/assets/erdos-1038-potential-landscape.mp4` as the source.
- Track only the final GIF, README, design, and plan.
- Do not add unrelated untracked scripts or `tmp/`.

---

### Task 1: Produce and Inspect the Hero GIF

**Files:**
- Create: `docs/showcase/assets/erdos-1038-potential-landscape.gif`
- Generate only: `.tmp-runs/erdos-1038-readme-contact-sheet.png`

**Interfaces:**
- Consumes: the committed 79-second H.264 MP4.
- Produces: a 21.9-second, 720px, 10fps GIF without the nearly empty transition.

- [ ] Run:

```powershell
ffmpeg -y -i docs/showcase/assets/erdos-1038-potential-landscape.mp4 -filter_complex "[0:v]trim=start=54:end=72,setpts=PTS-STARTPTS[a];[0:v]trim=start=75:end=78.9,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,fps=10,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" docs/showcase/assets/erdos-1038-potential-landscape.gif
```

- [ ] Probe duration, size, dimensions, and frame rate with `ffprobe`.
- [ ] Extract a six-frame contact sheet into `.tmp-runs/`.
- [ ] Inspect the contact sheet and reject dark frames, clipping, or unreadable formulas.

### Task 2: Add the README Hero

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: the accepted GIF, full MP4, and production prompt.
- Produces: the first animated README feature.

- [ ] Insert the centered GIF immediately before `traitor-axis.gif`.
- [ ] Add three plain-language paragraphs explaining roots as terrain, the
      zero plane, and the two extreme widths.
- [ ] Add links to the full MP4 and
      `docs/prompts/erdos-1038-off-white-3d.md`.
- [ ] Verify the first `.gif` reference in `README.md` is the Erdős hero and
      that the star-history URL remains present.

### Task 3: Verify and Publish

**Files:**
- Verify: `README.md`
- Verify: `docs/showcase/assets/erdos-1038-potential-landscape.gif`

**Interfaces:**
- Produces: one scoped commit pushed directly to `origin/main`.

- [ ] Run `git diff --check`.
- [ ] Run the prompt contract test.
- [ ] Stage only the README, GIF, design, and plan.
- [ ] Commit with `docs: feature Erdos 1038 film`.
- [ ] Push `main` to `origin/main`.
