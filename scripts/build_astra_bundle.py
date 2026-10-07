"""Build a public Astra distribution bundle from checked packages and film evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_film(paper, film_dir):
    manifest = json.loads((film_dir / 'quasi-riemann-render-manifest.json').read_text())
    evidence = json.loads((film_dir / 'quasi-riemann-film-evidence.json').read_text())
    candidate = paper / 'candidate.json'
    scene_hash = hashlib.sha256(json.loads(candidate.read_text(encoding='utf-8'))['content'].encode()).hexdigest()
    if manifest['status'] != 'completed' or manifest['source_candidate_sha256'] != sha256(candidate):
        raise ValueError('Film must have a completed manifest bound to the retained candidate')
    movie = film_dir / 'quasi-riemann-720p.mp4'
    if sha256(movie) != manifest['video_sha256'] or evidence['video_sha256'] != manifest['video_sha256']:
        raise ValueError('Film bytes do not match the completed render')
    if evidence['rendered_source_sha256'] != scene_hash:
        raise ValueError('Film source does not match the retained scene')
    if manifest['review_status'] != 'not_reviewed':
        raise ValueError('Preserve this render-existing film\'s not_reviewed status')
    return manifest


def build_bundle(root, dist, film_dir):
    version = tomllib.loads((root / 'pyproject.toml').read_text())['project']['version']
    wheel = dist / f'math_to_manim-{version}-py3-none-any.whl'
    sdist = dist / f'math_to_manim-{version}.tar.gz'
    for path in (wheel, sdist):
        if not path.is_file():
            raise ValueError(f'Missing distribution: {path.name}')
    with zipfile.ZipFile(wheel) as package:
        for name in ('astra/bridge.mjs', 'astra/node/package.json', 'astra/node/package-lock.json'):
            if name not in package.namelist():
                raise ValueError(f'Wheel lacks the Astra runtime asset: {name}')
    paper = root / 'papers/quasi-riemann'
    manifest = validate_film(paper, film_dir)
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'stream=width,height,r_frame_rate',
        '-show_entries', 'format=duration', '-of', 'json', str(film_dir / 'quasi-riemann-720p.mp4')], text=True))
    stream = probe['streams'][0]
    if (stream['width'], stream['height'], stream['r_frame_rate']) != (1280, 720, '30/1'):
        raise ValueError('The bundled movie must be the completed 720p/30 fps delivery')
    entries = {
        'README.md': (root / 'docs/ASTRA_BUNDLE.md').read_bytes(),
        'LICENSE': (root / 'LICENSE').read_bytes(),
        f'packages/{wheel.name}': wheel.read_bytes(),
        f'packages/{sdist.name}': sdist.read_bytes(),
    }
    for name in ('package.json', 'package-lock.json'):
        entries[f'runtime/{name}'] = (root / 'astra/node' / name).read_bytes()
    for name in ('quasi-riemann-720p.mp4', 'quasi-riemann-contact-sheet.png',
                 'quasi-riemann-render-manifest.json', 'quasi-riemann-film-evidence.json'):
        entries[f'films/{name}'] = (film_dir / name).read_bytes()
    # Enumerate tracked episode evidence, never arbitrary workspace files or runs.
    tracked = subprocess.check_output(['git', 'ls-files', '-z', 'papers/quasi-riemann'], cwd=root)
    for name in tracked.decode().split('\0'):
        if name:
            entries[name] = (root / name).read_bytes()
    for name in ('ASTRA_PIPELINE.md', 'JEV.md'):
        entries[f'docs/{name}'] = (root / 'docs' / name).read_bytes()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    record = dict(schema_version=1, distribution='math-to-manim-astra-bundle', version=version,
                  source_commit=commit, model='gpt-6-astra', codex_version='0.156.1',
                  primary_commands=['math-to-manim', 'math-to-manim-astra', 'm2m'],
                  film=dict(video='films/quasi-riemann-720p.mp4', video_sha256=manifest['video_sha256'],
                            candidate_sha256=manifest['source_candidate_sha256'],
                            review_status=manifest['review_status'], metadata=probe))
    entries['bundle.json'] = (json.dumps(record, indent=2) + '\n').encode()
    entries['SHA256SUMS.txt'] = ''.join(
        f'{hashlib.sha256(data).hexdigest()}  {name}\n' for name, data in sorted(entries.items())).encode()
    archive = dist / f'math-to-manim-astra-bundle-{version}.zip'
    prefix = f'math-to-manim-astra-{version}/'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in sorted(entries.items()):
            bundle.writestr(prefix + name, data)
    (dist / 'SHA256SUMS.txt').write_text(''.join(
        f'{sha256(path)}  {path.name}\n' for path in (wheel, sdist, archive)), encoding='utf-8')
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist', type=Path, default=Path('dist'))
    parser.add_argument('--film-dir', type=Path, required=True)
    args = parser.parse_args()
    print(build_bundle(Path(__file__).resolve().parents[1], args.dist.resolve(), args.film_dir.resolve()))
