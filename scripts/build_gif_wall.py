"""Compose earlier rendered films into the root README's animated GIF wall.

Each tile is an 8 second loop cut from a GIF that is already in the repo.
Requires FFmpeg with drawtext. No rendering agents or model calls are used.

    python scripts/build_gif_wall.py --font C:/Windows/Fonts/seguisb.ttf
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = 'docs/showcase/assets/gif-wall.gif'
SHOWCASE = 'docs/showcase/assets/'
COLUMNS = 4
TILE_W, TILE_H = 240, 135        # picture
LABEL_H, GUTTER = 21, 4          # label strip above the picture, space around it
SECONDS, FPS, COLORS = 8, 10, 128
INK, PAPER = '0xDDE9F5', '0x071426'

# (source GIF, start second, label). Order is row by row, newest films first.
TILES = [
    ('docs/assets/riemann-hypothesis-2026/riemann-hypothesis-2026.gif', 11, 'THETA LIFTS TO THE CRITICAL LINE'),
    ('docs/assets/base12-computer/base12-computer-journey.gif', 0, 'BASE 12 COMPUTER'),
    (SHOWCASE + 'score-sde-consistency.gif', 24, 'SCORE SDES TO CONSISTENCY'),
    (SHOWCASE + 'every-orbit-great-circle.gif', 7, 'EVERY ORBIT IS A GREAT CIRCLE'),
    (SHOWCASE + 'astra-morse-torus.gif', 8, 'MORSE THEORY ON A TORUS'),
    (SHOWCASE + 'mahler-film.gif', 8, 'THE SHAPE AND ITS SHADOW'),
    (SHOWCASE + 'the-third-side.gif', 12, 'THE THIRD SIDE'),
    ('docs/assets/loose-switch/loose-switch-journey.gif', 3, 'EVERY DIAL HAS A LOOSE SWITCH'),
    (SHOWCASE + 'traitor-axis.gif', 52, 'THE TRAITOR AXIS'),
    (SHOWCASE + 'exceptional-point-monodromy.gif', 0, 'EXCEPTIONAL POINT'),
    (SHOWCASE + 'the-valley.gif', 20, 'THE VALLEY'),
    (SHOWCASE + 'vortex-leapfrog.gif', 16, 'VORTEX'),
    (SHOWCASE + 'associate-family-riso.gif', 8, 'THE ASSOCIATE FAMILY'),
    (SHOWCASE + 'blueprint-holonomy.gif', 24, 'HOLONOMY'),
    (SHOWCASE + 'the-last-day.gif', 40, 'THE LAST DAY'),
    (SHOWCASE + 'qed-minkowski-epic-3d.gif', 12, 'QED IN MINKOWSKI SPACETIME'),
    (SHOWCASE + 'hopf-fibration.gif', 0, 'HOPF FIBRATION'),
    (SHOWCASE + 'lorenz-attractor.gif', 0, 'LORENZ ATTRACTOR'),
    (SHOWCASE + 'rhombicosidodecahedron.gif', 0, 'RHOMBICOSIDODECAHEDRON'),
    (SHOWCASE + 'circle-area-3d-unwrapped.gif', 10, 'AREA OF A CIRCLE'),
]


def ffmpeg_path(path):
    """A path that is safe inside an FFmpeg filter argument."""
    return path.resolve().as_posix().replace(':', r'\:')


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root')
    parser.add_argument('--out', type=Path, default=None, help=f'Output GIF (default {OUT})')
    parser.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/seguisb.ttf'),
                        help='Path to a TrueType font for the tile labels')
    args = parser.parse_args()
    if not args.font.is_file():
        parser.error('Supply --font with an installed TrueType font path')
    out = args.out or args.root / OUT
    font = ffmpeg_path(args.font)
    cell_w, cell_h = TILE_W + 2 * GUTTER, TILE_H + LABEL_H + 2 * GUTTER

    with tempfile.TemporaryDirectory(prefix='m2m-wall-') as scratch:
        scratch = Path(scratch)
        tiles = []
        for index, (source, start, label) in enumerate(TILES):
            text = scratch / f'{index}.txt'
            text.write_text(f'{index + 1:02d}  {label}', encoding='utf-8')
            tile = scratch / f'{index}.mp4'
            look = (f'fps={FPS},scale={TILE_W}:{TILE_H}:force_original_aspect_ratio=increase:flags=lanczos,'
                    f'crop={TILE_W}:{TILE_H},'
                    f'pad={cell_w}:{cell_h}:{GUTTER}:{GUTTER + LABEL_H}:color={PAPER},'
                    f"drawtext=fontfile='{font}':textfile='{ffmpeg_path(text)}':"
                    f'x={GUTTER + 2}:y={GUTTER + 4}:fontsize=11:fontcolor={INK}')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-ignore_loop', '1',
                            '-i', str(args.root / source), '-ss', str(start), '-t', str(SECONDS),
                            '-vf', look, '-an', '-c:v', 'libx264', '-crf', '14',
                            '-pix_fmt', 'yuv420p', str(tile)], check=True)
            tiles.append(tile)

        command = ['ffmpeg', '-v', 'error', '-y']
        for tile in tiles:
            command += ['-i', str(tile)]
        layout = '|'.join(f'{(i % COLUMNS) * cell_w}_{(i // COLUMNS) * cell_h}'
                          for i in range(len(tiles)))
        grid = (''.join(f'[{i}:v]' for i in range(len(tiles)))
                + f'xstack=inputs={len(tiles)}:layout={layout}:fill={PAPER}')
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(command + ['-filter_complex', grid +
                                  f',split[a][b];[a]palettegen=max_colors={COLORS}:stats_mode=diff[p];'
                                  '[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                                  '-loop', '0', str(out)], check=True)
    print(f'{out} {out.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
