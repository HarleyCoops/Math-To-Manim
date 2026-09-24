"""Local rendering of statically screened scene code; no model credentials inherited."""
import ast
import json
from pathlib import Path
import subprocess
import sys

from astra.client import clean_environment


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
    if classes != ['AstraFilm']:
        raise ValueError("Expected one ThreeDScene named AstraFilm")
    if 'self.camera.animate' in source:
        raise ValueError("Use move_camera instead of self.camera.animate")
    return tree


def command(args, *, cwd, timeout=120):
    result = subprocess.run(args, cwd=cwd, env=clean_environment(), capture_output=True,
                            text=True, encoding='utf-8', errors='replace', timeout=timeout)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[-5000:])
    return result.stdout


def render(run_dir, source, quality, attempt):
    validate_source(source)
    folder = Path(run_dir) / f'renders/{attempt:03d}'
    folder.mkdir(parents=True, exist_ok=False)
    (folder / 'scene.py').write_text(source, encoding='utf-8')
    args = [sys.executable, '-m', 'manim', f'-q{quality}', '--disable_caching',
            '--media_dir', str(folder / 'media'), '--progress_bar', 'none',
            str(folder / 'scene.py'), 'AstraFilm']
    proc = subprocess.run(args, cwd=folder, env=clean_environment(), capture_output=True,
                          text=True, encoding='utf-8', errors='replace', timeout=1800)
    (folder / 'stdout.log').write_text(proc.stdout, encoding='utf-8')
    (folder / 'stderr.log').write_text(proc.stderr, encoding='utf-8')
    if proc.returncode:
        raise RuntimeError(proc.stderr[-5000:])
    videos = [p for p in folder.rglob('AstraFilm.mp4') if 'partial_movie_files' not in p.parts]
    if len(videos) != 1 or videos[0].stat().st_size < 1024:
        raise RuntimeError('Render did not produce a unique final MP4')
    video = videos[0]
    metadata = json.loads(command(['ffprobe','-v','error','-show_entries',
                                   'format=duration:stream=width,height','-of','json',str(video)],cwd=folder))
    duration = float(metadata['format']['duration'])
    if not 20 <= duration <= 240:
        raise RuntimeError(f'Unexpected film duration: {duration}')
    frames = []
    for i in range(12):
        frame = folder / f'frame_{i:02d}.png'
        command(['ffmpeg','-v','error','-y','-ss',str(duration*(i+.5)/12),'-i',str(video),
                 '-frames:v','1',str(frame)],cwd=folder)
        if not frame.is_file():
            raise RuntimeError('Frame extraction produced no image')
        frames.append(frame)
    from PIL import Image, ImageOps, ImageDraw
    sheet = Image.new('RGB',(1280, 4*204),(12,18,30))
    for i, frame in enumerate(frames):
        with Image.open(frame) as img:
            thumb=ImageOps.contain(img,(426,180)); sheet.paste(thumb,((i%3)*426,(i//3)*204))
        ImageDraw.Draw(sheet).text(((i%3)*426+8,(i//3)*204+182),f'{duration*(i+.5)/12:.1f}s',fill='white')
    sheet.save(folder/'contact_sheet.png')
    (folder/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    return video, frames, folder/'contact_sheet.png'


def probe(run_dir, source, attempt):
    """Execute a candidate to a real final still; this is not a finished movie."""
    import hashlib
    validate_source(source)
    folder=Path(run_dir)/f'probes/{attempt:03d}'
    folder.mkdir(parents=True,exist_ok=False)
    scene=folder/'scene.py'
    scene.write_text(source,encoding='utf-8')
    result=subprocess.run([sys.executable,'-m','manim','-s','--disable_caching',
        '--media_dir',str(folder/'media'),'--progress_bar','none',str(scene),'AstraFilm'],
        cwd=folder,env=clean_environment(),capture_output=True,text=True,
        encoding='utf-8',errors='replace',timeout=600)
    (folder/'stdout.log').write_text(result.stdout,encoding='utf-8')
    (folder/'stderr.log').write_text(result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError('Scene execution probe failed: '+result.stderr[-5000:])
    frames=list((folder/'media/images/scene').glob('AstraFilm*.png'))
    if len(frames)!=1:raise RuntimeError('Scene probe did not produce exactly one image')
    record=folder/'execution.json'
    record.write_text(json.dumps({'kind':'actual_manim_final_frame_probe',
        'source_sha256':hashlib.sha256(source.encode('utf-8')).hexdigest(),
        'exit_code':result.returncode,'image':frames[0].relative_to(run_dir).as_posix(),
        'limitations':['Final still only; no continuous movie rendered or inspected.']},indent=2),encoding='utf-8')
    return record,frames[0]
