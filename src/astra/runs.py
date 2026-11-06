"""Layout of runs/astra: run folders, attempt files, manifests and file helpers.

Resolved when asked, never at import: an installed package writes runs/astra
under the working directory it is run from.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import uuid

from astra.client import MODEL
from astra.jev import evaluator_name

RUN_ID = re.compile(r'\d{8}-\d{6}-[0-9a-f]{6}')
ATTEMPT_FILE = re.compile(r'(\d{3})-([a-z]+)-([a-z-]+)\.json')


def runs_root(base=None):
    return Path(base or Path.cwd()) / 'runs' / 'astra'


def new_run_id():
    return datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]


def is_run_id(name):
    return RUN_ID.fullmatch(name) is not None


def run_folder(run_id):
    """An existing run created by this pipeline; anything else is rejected before any read."""
    if not is_run_id(run_id):
        raise ValueError('Expected an Astra run ID')
    root = runs_root().resolve()
    folder = (root / run_id).resolve()
    if folder.parent != root or not folder.is_dir():
        raise ValueError('Unknown Astra run')
    return folder


def list_runs():
    """(folder name, manifest) for every run folder holding a readable manifest, oldest first."""
    runs = []
    for path in sorted(runs_root().glob('*/manifest.json')):
        try:
            runs.append((path.parent.name, json.loads(path.read_text(encoding='utf-8'))))
        except (OSError, ValueError):
            continue
    return runs


def create_run(request, runs_dir=None):
    """A new run folder holding the request and a queued manifest; returns (folder, manifest)."""
    folder = Path(runs_dir or runs_root()) / new_run_id()
    folder.mkdir(parents=True)
    save(folder / 'request.json', request.model_dump())
    manifest = dict(status='queued', run_id=folder.name, run_dir=str(folder), model=MODEL,
                    evaluator=evaluator_name(request.review_mode),
                    review_mode=request.review_mode, stages={}, events=[])
    save(folder / 'manifest.json', manifest)
    return folder, manifest


def attempt_path(folder, index, stage, kind):
    """attempts/{NNN}-{stage}-{kind}.json: every retained per-attempt record."""
    return Path(folder) / 'attempts' / f'{index:03d}-{stage}-{kind}.json'


def attempt_paths(folder, kind, *, stage='*', index=None):
    """Retained attempt records of one kind, in attempt order."""
    prefix = f'{index:03d}' if index is not None else '[0-9][0-9][0-9]'
    return sorted((Path(folder) / 'attempts').glob(f'{prefix}-{stage}-{kind}.json'))


def parse_attempt(path):
    """(index, stage, kind) of an attempt record, or None for sidecar files."""
    match = ATTEMPT_FILE.fullmatch(Path(path).name)
    return (int(match[1]), match[2], match[3]) if match else None


def attempt_index(path):
    """The attempt number any file under attempts/ was written for."""
    head = Path(path).name.split('-')[0]
    return int(head) if head.isdigit() else None


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
    temp.replace(path)
