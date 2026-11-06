"""Host-owned render entry point: delivery settings override scene-level defaults."""
import runpy
import sys
from pathlib import Path

PROFILES = {'l': (854, 480, 15), 'm': (1280, 720, 30), 'h': (1920, 1080, 60)}


def main(source, media_dir, quality, mode='movie'):
    from manim import tempconfig
    # Load the screened source first so its config cannot override user quality.
    scene_class = runpy.run_path(str(Path(source).resolve()))['AstraFilm']
    width, height, fps = PROFILES[quality]
    with tempconfig({'pixel_width': width, 'pixel_height': height, 'frame_rate': fps,
                     'renderer': 'cairo', 'media_dir': str(Path(media_dir).resolve()),
                     'output_file': 'AstraFilm', 'write_to_movie': mode=='movie',
                     'save_last_frame': mode=='still', 'disable_caching': True,
                     'progress_bar': 'none'}):
        scene_class().render()


if __name__ == '__main__':
    main(*sys.argv[1:])
