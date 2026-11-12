"""Local rendering of statically screened scene code; no model credentials inherited."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from astra.environment import clean_environment
from astra.render_worker import PROFILES

WORKER = Path(__file__).with_name('render_worker.py')
SCENE_CLASS = 'AstraFilm'
FILM_DURATION = (20, 240)   # seconds; the ordinary film budget, overridable per delivery
FRAME_COUNT = 12


def validate_source(source):
    tree = ast.parse(source)
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            if any(name.split('.')[0] not in {"manim", "numpy", "math"} for name in names):
                raise ValueError("Scene imports must be manim, numpy, or math")
        if isinstance(node, ast.Attribute) and node.attr.startswith('__'):
            raise ValueError("Scene cannot access dunder attributes")
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, 'attr', '')
            if name in {"eval", "exec", "compile", "open", "__import__", "getattr", "setattr",
                        "load", "save", "loadtxt", "savetxt", "fromfile", "tofile", "memmap"}:
                raise ValueError(f"Scene contains prohibited call: {name}")
        if isinstance(node, ast.ClassDef) and any(isinstance(b, ast.Name) and b.id == 'ThreeDScene' for b in node.bases):
            classes.append(node.name)
    if classes != [SCENE_CLASS]:
        raise ValueError(f"Expected one ThreeDScene named {SCENE_CLASS}")
    if 'self.camera.animate' in source:
        raise ValueError("Use move_camera instead of self.camera.animate")
    return tree


def command(args, *, cwd, timeout=120):
    result = subprocess.run(args, cwd=cwd, env=clean_environment(), capture_output=True,
                            text=True, encoding='utf-8', errors='replace', timeout=timeout)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[-5000:])
    return result.stdout


def run_worker(folder, source, quality, mode, *, timeout):
    """Execute screened source in a fresh folder with the host-owned worker; logs are retained."""
    validate_source(source)
    folder.mkdir(parents=True, exist_ok=False)
    scene = folder / 'scene.py'
    scene.write_text(source, encoding='utf-8')
    proc = subprocess.run([sys.executable, str(WORKER), str(scene), str(folder / 'media'), quality, mode],
                          cwd=folder, env=clean_environment(), capture_output=True,
                          text=True, encoding='utf-8', errors='replace', timeout=timeout)
    (folder / 'stdout.log').write_text(proc.stdout, encoding='utf-8')
    (folder / 'stderr.log').write_text(proc.stderr, encoding='utf-8')
    return proc


class DeliveryError(RuntimeError):
    """The renderer, not the scene source, produced the wrong delivery profile."""


def check_delivery(metadata, quality):
    """The movie must be exactly the requested silent delivery profile."""
    width, height, fps = PROFILES[quality]
    streams = metadata['streams']
    video = [s for s in streams if s['codec_type'] == 'video']
    if len(video) != 1 or (video[0]['width'], video[0]['height']) != (width, height):
        raise DeliveryError('Wrong delivery dimensions')
    if video[0]['r_frame_rate'] != f'{fps}/1':
        raise DeliveryError('Wrong frame rate')
    if any(s['codec_type'] == 'audio' for s in streams):
        raise RuntimeError('Unexpected audio')


def render_folder(run_dir, attempt):
    return Path(run_dir) / 'renders' / f'{attempt:03d}'


def next_render_attempt(run_dir):
    return max([int(p.name) for p in (Path(run_dir) / 'renders').glob('*') if p.name.isdigit()] + [0]) + 1


def render(run_dir, source, quality, attempt, *, duration_range=FILM_DURATION):
    folder = render_folder(run_dir, attempt)
    # Detailed 1080p/60 fps Cairo surfaces can exceed thirty minutes locally.
    proc = run_worker(folder, source, quality, 'movie', timeout=7200)
    if proc.returncode:
        raise RuntimeError(proc.stderr[-5000:])
    videos = [p for p in folder.rglob(f'{SCENE_CLASS}.mp4') if 'partial_movie_files' not in p.parts]
    if len(videos) != 1 or videos[0].stat().st_size < 1024:
        raise RuntimeError('Render did not produce a unique final MP4')
    video = videos[0]
    metadata = json.loads(command(['ffprobe','-v','error','-show_entries',
                                   'format=duration:stream=codec_type,width,height,r_frame_rate','-of','json',str(video)],cwd=folder))
    duration = float(metadata['format']['duration'])
    low, high = duration_range
    if not low <= duration <= high:
        raise RuntimeError(f'Unexpected film duration: {duration}')
    check_delivery(metadata, quality)
    frames = []
    for i in range(FRAME_COUNT):
        frame = folder / f'frame_{i:02d}.png'
        command(['ffmpeg','-v','error','-y','-ss',str(duration*(i+.5)/FRAME_COUNT),'-i',str(video),
                 '-frames:v','1',str(frame)],cwd=folder)
        if not frame.is_file():
            raise RuntimeError('Frame extraction produced no image')
        frames.append(frame)
    from PIL import Image, ImageOps, ImageDraw
    sheet = Image.new('RGB',(1280, 4*204),(12,18,30))
    for i, frame in enumerate(frames):
        with Image.open(frame) as img:
            thumb=ImageOps.contain(img,(426,180)); sheet.paste(thumb,((i%3)*426,(i//3)*204))
        ImageDraw.Draw(sheet).text(((i%3)*426+8,(i//3)*204+182),f'{duration*(i+.5)/FRAME_COUNT:.1f}s',fill='white')
    sheet.save(folder/'contact_sheet.png')
    (folder/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    return video, frames, folder/'contact_sheet.png'


def probe(run_dir, source, attempt, quality):
    """Execute a candidate to a real final still at the delivery quality; this is not a finished movie."""
    folder=Path(run_dir)/f'probes/{attempt:03d}'
    proc=run_worker(folder, source, quality, 'still', timeout=600)
    if proc.returncode:raise RuntimeError('Scene execution probe failed: '+proc.stderr[-5000:])
    frames=list((folder/'media/images').rglob(f'{SCENE_CLASS}*.png'))
    if len(frames)!=1:raise RuntimeError('Scene probe did not produce exactly one image')
    record=folder/'execution.json'
    from PIL import Image
    with Image.open(frames[0]) as image:
        resolution=list(image.size)
    record.write_text(json.dumps({'kind':'actual_manim_final_frame_probe',
        'source_sha256':hashlib.sha256(source.encode('utf-8')).hexdigest(),
        'delivery_quality':quality,'resolution':resolution,
        'exit_code':proc.returncode,'image':frames[0].relative_to(run_dir).as_posix(),
        'limitations':['Final still only; no continuous movie rendered or inspected.']},indent=2),encoding='utf-8')
    return record,frames[0]
