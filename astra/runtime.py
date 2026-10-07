"""Install the locked Codex runtime in a user-writable cache for wheel installs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


ASSETS = Path(__file__).with_name('node')
REPOSITORY = Path(__file__).resolve().parents[1]
CODEX_VERSION = '0.156.1'


def cache_directory():
    if os.name == 'nt':
        base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
    else:
        base = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
    lock_hash = hashlib.sha256((ASSETS / 'package-lock.json').read_bytes()).hexdigest()[:16]
    return base / 'math-to-manim' / f'codex-{CODEX_VERSION}-{lock_hash}'


def is_installed(folder):
    for package in ('codex', 'codex-sdk'):
        path = folder / f'node_modules/@openai/{package}/package.json'
        try:
            if json.loads(path.read_text(encoding='utf-8'))['version'] != CODEX_VERSION:
                return False
        except (OSError, ValueError, KeyError):
            return False
    return (folder / 'node_modules/@openai/codex/bin/codex.js').is_file()


def runtime_directory():
    # Keep an existing source installation working, including its pinned runtime.
    if is_installed(REPOSITORY):
        return REPOSITORY
    cached = cache_directory()
    if is_installed(cached):
        return cached
    raise RuntimeError('Codex runtime missing. Run: math-to-manim setup')


def setup_runtime():
    from astra.client import clean_environment

    npm = shutil.which('npm')
    if not npm or not shutil.which('node'):
        raise RuntimeError('Install Node.js 18+ and npm, then run: math-to-manim setup')
    cached = cache_directory()
    cached.mkdir(parents=True, exist_ok=True)
    for name in ('package.json', 'package-lock.json'):
        shutil.copyfile(ASSETS / name, cached / name)
    subprocess.run([npm, 'ci', '--no-audit', '--no-fund'], cwd=cached,
                   env=clean_environment(), check=True, timeout=600)
    if not is_installed(cached):
        raise RuntimeError('The pinned Codex runtime did not install successfully')
    return cached


def codex_command(*args):
    node = shutil.which('node')
    if not node:
        raise RuntimeError('Install Node.js 18+ and npm, then run: math-to-manim setup')
    return [node, str(runtime_directory() / 'node_modules/@openai/codex/bin/codex.js'), *args]
