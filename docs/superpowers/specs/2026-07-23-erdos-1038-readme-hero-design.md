# Erdős 1038 README Hero Design

## Goal

Make the Erdős 1038 film the first animation on the root README and explain
its mathematical idea in approachable language for readers who do not know
potential theory.

## Media

- Source: `docs/showcase/assets/erdos-1038-potential-landscape.mp4`
- Hero GIF: `docs/showcase/assets/erdos-1038-potential-landscape.gif`
- Selected intervals: 54–72 seconds and 75–78.9 seconds
- Output: 720 pixels wide, 10 frames per second, palette-optimized

The selected interval contains the certified lower value, the explanation of
why the curve alone is not the proof, the endpoint construction for the upper
value, and the final off-white 3D tableau. The nearly empty transition between
the endpoint construction and final tableau is removed, producing a
21.9-second hero loop.

## README Placement

Preserve the star-history chart, title, badges, navigation, and introductory
quotation. Insert the Erdős GIF immediately after that introduction and before
the existing Traitor Axis feature, making it the first animation on the page.

## Copy

The explanation uses three short plain-language paragraphs:

1. A polynomial is determined by its roots, and its size along the number line
   can be pictured as a landscape carved by those roots.
2. The transparent zero plane turns the abstract inequality `|f(x)| < 1` into
   visible terrain: the desired set is exactly the portion lying below the
   plane. Moving and combining roots changes the width of that submerged
   region.
3. The narrowest possible shape is approached by increasingly fine root
   distributions and has width `1.834430475762661…`; the widest shape places
   all roots at the endpoints and has width `2√2`.

Avoid proof jargon in the main prose. Link readers to the full MP4 and the
complete production prompt for technical details.

## Acceptance

- The GIF is visually inspected through a contact sheet.
- It remains off-white, recognizably 3D, and readable at README width.
- The root README retains its star chart and existing showcase content.
- The GIF is the first animation on the page.
- The full MP4 and prompt links resolve to tracked repository files.
