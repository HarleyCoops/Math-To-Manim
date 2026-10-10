"""Render the longer pi explainer with Math-To-Manim's existing Manim worker.

The ordinary retained-scene renderer caps movies at 240 seconds. This episode
has an explicit 280–420-second reading budget; its delivery helper retains the
same source screening, credential-free worker and real render evidence.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

from astra.client import clean_environment
from astra.pipeline import digest, save
from astra.rendering import command, validate_source
from astra.render_worker import PROFILES

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--authoring-run', type=Path,
                        help='Optional local authoring run; otherwise verify the retained production record')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--quality', choices=PROFILES, default='m')
    args = parser.parse_args()
    candidate, output = args.candidate.resolve(), args.output.resolve()
    authoring = args.authoring_run.resolve() if args.authoring_run else None
    if candidate.parent != ROOT / 'papers/pi-approximations':
        raise ValueError('Expected the retained pi episode candidate')
    if (authoring is not None and authoring.parent != ROOT / 'runs/astra') or output.parent != ROOT / 'runs/astra':
        raise ValueError('Expected direct Astra run folders')
    if authoring is not None:
        original = json.loads((authoring / 'manifest.json').read_text(encoding='utf-8'))
        if original['status'] != 'completed':
            raise ValueError('Authoring must be completed before delivery')
        if candidate.read_bytes() != (authoring / 'scene.json').read_bytes():
            raise ValueError('Candidate must exactly match the completed authored scene')
        authoring_id = authoring.name
    else:
        original = json.loads((candidate.parent / 'production.json').read_text(encoding='utf-8'))
        if original.get('authoring_status') != 'completed' or original.get('candidate_sha256') != digest(candidate):
            raise ValueError('Candidate must match its completed retained authoring record')
        authoring_id = original['run_id']
    source = json.loads(candidate.read_text(encoding='utf-8'))['content']
    validate_source(source)
    output.mkdir(parents=True, exist_ok=False)
    if authoring is not None:
        for name in ('brief.json', 'mathematics.json', 'storyboard.json', 'scene.json',
                     'request.json', 'operator-delivery-brief.json'):
            shutil.copy2(authoring / name, output / name)
    else:
        shutil.copy2(candidate, output / 'scene.json')
        shutil.copy2(candidate.parent / 'production.json', output / 'source-provenance.json')
    folder = output / 'renders/001'
    folder.mkdir(parents=True)
    scene = folder / 'scene.py'
    scene.write_text(source, encoding='utf-8')
    ledger = dict(status='rendering', model='gpt-6-astra', evaluator='disabled',
        execution='math_to_manim_render_worker', review_status='not_reviewed',
        authoring_run_id=authoring_id, run_id=output.name,
        candidate=candidate.relative_to(ROOT).as_posix(), candidate_sha256=digest(candidate),
        rendered_source=scene.relative_to(output).as_posix(), source_sha256=digest(scene),
        render_quality=args.quality, planned_duration_range_seconds=[280, 420],
        frame_quantization_tolerance_seconds=2, events=[])
    save(output / 'manifest.json', ledger)
    print('Rendering the retained pi scene with the Math-To-Manim Manim worker', flush=True)
    try:
        proc = subprocess.run([sys.executable, str(ROOT / 'astra/render_worker.py'),
            str(scene), str(folder / 'media'), args.quality], cwd=folder,
            env=clean_environment(), capture_output=True, text=True,
            encoding='utf-8', errors='replace', timeout=7200)
        (folder / 'stdout.log').write_text(proc.stdout, encoding='utf-8')
        (folder / 'stderr.log').write_text(proc.stderr, encoding='utf-8')
        if proc.returncode:
            raise RuntimeError(proc.stderr[-5000:])
        videos = [p for p in folder.rglob('AstraFilm.mp4') if 'partial_movie_files' not in p.parts]
        if len(videos) != 1 or videos[0].stat().st_size < 1024:
            raise RuntimeError('No unique complete movie')
        movie = videos[0]
        metadata = json.loads(command(['ffprobe', '-v', 'error', '-show_streams',
            '-show_format', '-of', 'json', str(movie)], cwd=folder))
        duration = float(metadata['format']['duration'])
        if not 280 <= duration <= 422:
            raise RuntimeError(f'Unexpected duration: {duration}')
        streams = metadata['streams']
        video_streams = [s for s in streams if s['codec_type'] == 'video']
        width, height, fps = PROFILES[args.quality]
        if len(video_streams) != 1 or (video_streams[0]['width'], video_streams[0]['height']) != (width, height):
            raise RuntimeError('Wrong delivery dimensions')
        if video_streams[0]['r_frame_rate'] != f'{fps}/1' or any(s['codec_type'] == 'audio' for s in streams):
            raise RuntimeError('Wrong frame rate or unexpected audio')
        from PIL import Image, ImageDraw, ImageOps
        sheet = Image.new('RGB', (1280, 4 * 204), '#202A35')
        for i in range(12):
            frame = folder / f'frame_{i:02d}.png'
            time = duration * (i + .5) / 12
            command(['ffmpeg', '-v', 'error', '-y', '-ss', str(time), '-i', str(movie),
                '-frames:v', '1', str(frame)], cwd=folder)
            with Image.open(frame) as image:
                thumb = ImageOps.contain(image.convert('RGB'), (426, 180))
                sheet.paste(thumb, ((i % 3) * 426, (i // 3) * 204))
            ImageDraw.Draw(sheet).text(((i % 3) * 426 + 8, (i // 3) * 204 + 182), f'{time:.1f}s', fill='white')
        sheet.save(folder / 'contact_sheet.png')
        save(folder / 'metadata.json', metadata)
        ledger.update(status='completed', video=movie.relative_to(output).as_posix(),
            video_sha256=digest(movie), contact_sheet=(folder / 'contact_sheet.png').relative_to(output).as_posix(),
            duration_seconds=duration, completed_utc=datetime.now(timezone.utc).isoformat())
    except Exception as exc:
        ledger.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        save(output / 'manifest.json', ledger)
    print(json.dumps(ledger, indent=2))


if __name__ == '__main__':
    main()
