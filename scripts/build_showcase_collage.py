"""Compose existing rendered samples into the root README's animated collage.

Requires FFmpeg with drawtext. No rendering agents or model calls are used.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'docs/showcase/assets'
SAMPLES = [
    ('astra-morse-torus.mp4', 47, '01  MORSE THEORY'),
    ('the-third-side.mp4', 18, '02  THE THIRD SIDE'),
    ('hopf-fibration.gif', 0, '03  HOPF FIBRATION'),
    ('blueprint-holonomy.gif', 24, '04  PARALLEL TRANSPORT'),
    ('rhombicosidodecahedron.gif', 0, '05  POLYHEDRAL GEOMETRY'),
    ('associate-family-riso.gif', 8, '06  MINIMAL SURFACES'),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/seguisb.ttf'),
                        help='Path to a TrueType font for panel labels')
    args = parser.parse_args()
    if not args.font.is_file():
        parser.error('Supply --font with an installed TrueType font path')
    font = args.font.resolve().as_posix().replace(':', r'\:')
    with tempfile.TemporaryDirectory(prefix='m2m-collage-') as scratch:
        tiles = []
        for index, (name, start, label) in enumerate(SAMPLES):
            tile = Path(scratch) / f'{index}.mp4'
            command = ['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1']
            if name.endswith('.gif'):
                command += ['-ignore_loop', '1']
            command += ['-i', str(ASSETS / name), '-ss', str(start), '-t', '8',
                '-vf', 'fps=12,scale=352:198:force_original_aspect_ratio=decrease,'
                       'pad=352:198:(ow-iw)/2:(oh-ih)/2:color=0x071426,'
                       'pad=368:234:8:28:color=0x071426,'
                       f"drawtext=fontfile='{font}':text='{label}':x=10:y=7:fontsize=13:fontcolor=0xDDE9F5",
                '-an', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', str(tile)]
            subprocess.run(command, check=True)
            tiles.append(tile)
        command = ['ffmpeg', '-v', 'error', '-y']
        for tile in tiles:
            command += ['-i', str(tile)]
        grid = ('[0:v][1:v][2:v][3:v][4:v][5:v]'
                'xstack=inputs=6:layout=0_0|368_0|736_0|0_234|368_234|736_234')
        subprocess.run(command + ['-filter_complex', grid, '-frames:v', '1',
                       str(ASSETS / 'showcase-collage-poster.png')], check=True)
        subprocess.run(command + ['-filter_complex', grid +
            ',split[a][b];[a]palettegen=max_colors=192[p];[b][p]paletteuse=dither=bayer',
            '-loop', '0', str(ASSETS / 'showcase-collage.gif')], check=True)


if __name__ == '__main__':
    main()
