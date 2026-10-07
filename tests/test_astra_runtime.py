"""Packaged installs resolve their pinned runtime without a repository checkout."""
import json
from pathlib import Path
import pytest
from astra import runtime


def installed_runtime(folder, version='0.156.1'):
    for name in ('codex', 'codex-sdk'):
        package = folder / f'node_modules/@openai/{name}'
        package.mkdir(parents=True)
        (package / 'package.json').write_text(json.dumps({'version': version}))
    cli = folder / 'node_modules/@openai/codex/bin/codex.js'
    cli.parent.mkdir()
    cli.write_text('')
    return folder


def test_wheel_runtime_resolves_from_cache(tmp_path, monkeypatch):
    cached = installed_runtime(tmp_path / 'cache')
    monkeypatch.setattr(runtime, 'REPOSITORY', tmp_path / 'absent-checkout')
    monkeypatch.setattr(runtime, 'cache_directory', lambda: cached)
    assert runtime.runtime_directory() == cached


def test_source_install_keeps_its_existing_runtime(tmp_path, monkeypatch):
    checkout = installed_runtime(tmp_path / 'source')
    monkeypatch.setattr(runtime, 'REPOSITORY', checkout)
    monkeypatch.setattr(runtime, 'cache_directory', lambda: pytest.fail('Source runtime is ready'))
    assert runtime.runtime_directory() == checkout


def test_wrong_version_requires_setup(tmp_path, monkeypatch):
    cached = installed_runtime(tmp_path / 'cache', version='0.156.0')
    monkeypatch.setattr(runtime, 'REPOSITORY', tmp_path / 'absent-checkout')
    monkeypatch.setattr(runtime, 'cache_directory', lambda: cached)
    with pytest.raises(RuntimeError, match='math-to-manim setup'):
        runtime.runtime_directory()


def test_setup_strips_credentials_and_installs_the_locked_runtime(tmp_path, monkeypatch):
    cached = tmp_path / 'cache'
    monkeypatch.setattr(runtime, 'cache_directory', lambda: cached)
    monkeypatch.setattr(runtime.shutil, 'which', lambda name: name)
    monkeypatch.setenv('OPENAI_API_KEY', 'test')
    monkeypatch.setenv('TYPESAFE_API_KEY', 'test')
    def install(command, **kwargs):
        assert command == ['npm', 'ci', '--no-audit', '--no-fund']
        assert 'OPENAI_API_KEY' not in kwargs['env'] and 'TYPESAFE_API_KEY' not in kwargs['env']
        assert (cached / 'package-lock.json').read_bytes() == (runtime.ASSETS / 'package-lock.json').read_bytes()
        installed_runtime(cached)
    monkeypatch.setattr(runtime.subprocess, 'run', install)
    assert runtime.setup_runtime() == cached


def test_packaged_lock_matches_the_repository():
    root = Path(__file__).resolve().parents[1]
    for name in ('package.json', 'package-lock.json'):
        assert json.loads((runtime.ASSETS / name).read_text()) == json.loads((root / name).read_text())
