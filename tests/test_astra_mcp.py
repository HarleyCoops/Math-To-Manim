"""Ensure the MCP front door preserves the real Astra/Jev pipeline boundary."""
import asyncio
import json
from pathlib import Path
import pytest

from astra import mcp_server as server
from astra.models import Request


def test_mcp_registry_uses_astra_and_typed_request():
    tools = {tool.name: tool for tool in asyncio.run(server.mcp.list_tools())}
    create = tools['m2m_create_animation']
    assert create.annotations.title == 'Create Astra/Jev Animation'
    schema = create.input_schema
    assert 'params' in schema['properties']
    assert {'m2m_get_job', 'm2m_list_runs', 'm2m_get_scene_code'} <= tools.keys()


def test_worker_keeps_request_and_separates_credentials(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(server, 'RUNS', tmp_path)
    monkeypatch.setattr(server, 'load_api_key', lambda: 'fake-jev-credential')
    monkeypatch.setenv('OPENAI_API_KEY', 'must-not-be-inherited')
    class Process:
        pid = 123
    def launch(args, **kwargs):
        calls.append((args, kwargs))
        return Process()
    monkeypatch.setattr(server.subprocess, 'Popen', launch)
    request = Request(prompt='Explain polar convex bodies', render=False, quality='m')
    state = json.loads(server.m2m_create_animation(request))
    args, options = calls[0]
    assert args[1:4] == ['-u', '-m', 'astra.job_worker']
    assert options['env']['TYPESAFE_API_KEY'] == 'fake-jev-credential'
    assert 'OPENAI_API_KEY' not in options['env']
    assert state['model'] == 'gpt-6-astra' and state['evaluator'] == 'jev-1.13.0'
    assert json.loads((Path(state['run_dir']) / 'request.json').read_text()) == request.model_dump()
    assert json.loads(server.m2m_get_job(state['run_id']))['status'] == 'queued'


def test_missing_jev_credential_consumes_no_model_calls(tmp_path, monkeypatch):
    monkeypatch.setattr(server, 'RUNS', tmp_path)
    def missing():
        raise RuntimeError('missing credential')
    monkeypatch.setattr(server, 'load_api_key', missing)
    with pytest.raises(RuntimeError, match='missing'):
        server.m2m_create_animation(Request(prompt='Explain polar convex bodies'))
    assert not list(tmp_path.iterdir())


def test_explicit_jev_off_needs_no_credential(tmp_path, monkeypatch):
    monkeypatch.setattr(server, 'RUNS', tmp_path)
    monkeypatch.setattr(server, 'load_api_key', lambda: pytest.fail('No Jev credential needed'))
    options = []
    class Process:
        pid = 123
    monkeypatch.setattr(server.subprocess, 'Popen', lambda *a, **kw: options.append(kw) or Process())
    state = json.loads(server.m2m_create_animation(Request(prompt='Explain polar convex bodies',review_mode='off')))
    assert state['evaluator']=='disabled' and 'TYPESAFE_API_KEY' not in options[0]['env']


def test_doctor_off_does_not_load_jev_credentials(monkeypatch):
    from astra.cli import main
    from subprocess import CompletedProcess
    monkeypatch.setattr('astra.cli.codex_command', lambda *args: ['codex', *args])
    monkeypatch.setattr('astra.cli.subprocess.run', lambda *a, **kw: CompletedProcess(a,0))
    monkeypatch.setattr('astra.jev.load_api_key', lambda: pytest.fail('Jev is off'))
    assert main(['doctor','--review-mode','off'])==0


def test_doctor_missing_runtime_reports_setup(monkeypatch, capsys):
    from astra.cli import main
    def missing(*args):
        raise RuntimeError('Codex runtime missing. Run: math-to-manim setup')
    monkeypatch.setattr('astra.cli.codex_command', missing)
    monkeypatch.setattr('astra.jev.load_api_key', lambda: pytest.fail('Runtime setup must precede Jev'))
    assert main(['doctor', '--review-mode', 'off']) == 1
    assert 'math-to-manim setup' in capsys.readouterr().out


@pytest.mark.parametrize('run_id', ['../other', 'C:/outside', 'wrong-provider'])
def test_run_reads_cannot_escape_astra_root(run_id):
    with pytest.raises(ValueError):
        server.m2m_get_job(run_id)
