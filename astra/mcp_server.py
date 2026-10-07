"""MCP front door to Astra's existing Codex SDK and real TypeSafe Jev chain."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from astra import __version__
from astra.client import clean_environment, MODEL
from astra.jev import JEV_MODEL, load_api_key
from astra.models import Artifact, Request
from astra.pipeline import ROOT, save

RUNS = ROOT / 'runs/astra'
mcp = MCPServer('math_to_manim_astra', version=__version__,
    description='Codex SDK Astra authors and auditors, with real TypeSafe Jev reviews.')


def run_folder(run_id):
    if not re.fullmatch(r'\d{8}-\d{6}-[0-9a-f]{6}', run_id):
        raise ValueError('Expected an Astra run ID')
    root = RUNS.resolve()
    folder = (root / run_id).resolve()
    if folder.parent != root or not folder.is_dir():
        raise ValueError('Unknown Astra run')
    return folder


@mcp.tool(annotations=ToolAnnotations(title='Create Astra/Jev Animation',
    read_only_hint=False, destructive_hint=False, open_world_hint=True))
def m2m_create_animation(params: Request) -> str:
    """Start the actual Astra/Jev pipeline while the MCP server remains running.

    Reviews are advisory by default. No alternate provider or evaluator fallback.
    Inspect m2m_get_job for progress and retained review/render evidence.
    Keep the server alive until completion; Windows MCP clients own its process tree.
    """
    key = load_api_key() if params.review_mode != 'off' else None
    run_id = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
    folder = RUNS / run_id
    folder.mkdir(parents=True)
    save(folder / 'request.json', params.model_dump())
    state = dict(status='queued', run_id=run_id, run_dir=str(folder), model=MODEL,
                 evaluator=JEV_MODEL if key is not None else 'disabled',
                 review_mode=params.review_mode, stages={}, events=[])
    save(folder / 'manifest.json', state)
    # This worker owns the Jev credential. Codex SDK and renderer descendants
    # still use the existing clean_environment() contract, stripping API keys.
    env = clean_environment()
    if key is not None:
        env['TYPESAFE_API_KEY'] = key
    options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
    try:
        with (folder / 'worker.log').open('ab') as log:
            proc = subprocess.Popen([sys.executable, '-u', '-m', 'astra.job_worker', str(folder)],
                cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log, **options)
    except Exception:
        state.update(status='failed', error='Worker could not start')
        save(folder / 'manifest.json', state)
        raise
    save(folder / 'worker.json', {'pid': proc.pid})
    return json.dumps(state)


@mcp.tool(annotations=ToolAnnotations(title='Inspect Astra Job',
    read_only_hint=True, idempotent_hint=True, open_world_hint=False))
def m2m_get_job(run_id: str) -> str:
    """Read the durable run manifest, including actual Jev verdicts and MP4 hash."""
    return (run_folder(run_id) / 'manifest.json').read_text(encoding='utf-8')


@mcp.tool(annotations=ToolAnnotations(title='List Astra Runs',
    read_only_hint=True, idempotent_hint=True, open_world_hint=False))
def m2m_list_runs() -> str:
    """List Astra manifests without triggering model calls or renders."""
    runs = []
    for path in sorted(RUNS.glob('*/manifest.json'), reverse=True):
        if re.fullmatch(r'\d{8}-\d{6}-[0-9a-f]{6}', path.parent.name):
            state = json.loads(path.read_text(encoding='utf-8'))
            runs.append({'run_id': path.parent.name, 'status': state['status'],
                         'review_status': state.get('review_status')})
    return json.dumps(runs)


@mcp.tool(annotations=ToolAnnotations(title='Read Astra Scene',
    read_only_hint=True, idempotent_hint=True, open_world_hint=False))
def m2m_get_scene_code(run_id: str) -> str:
    """Read the retained scene candidate; source alone does not imply a movie exists."""
    folder = run_folder(run_id)
    return Artifact.model_validate_json((folder / 'scene.json').read_text(encoding='utf-8')).content


def main(transport='stdio', port=8644):
    if transport == 'stdio':
        mcp.run()
    else:
        mcp.run(transport='streamable-http', host='127.0.0.1', port=port)


if __name__ == '__main__':
    main()
