from __future__ import annotations

from math_to_manim.config import RuntimeConfig


def test_runtime_config_loads_local_env_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("M2M2_MODEL", raising=False)
    monkeypatch.delenv("M2M2_RUNS_DIR", raising=False)
    (tmp_path / ".env").write_text("M2M2_MODEL=test-model\nM2M2_RUNS_DIR=custom-runs\n", encoding="utf-8")

    config = RuntimeConfig.from_env()

    assert config.model == "test-model"
    assert str(config.runs_dir) == "custom-runs"


def test_runtime_config_defaults_mythos_to_fugu(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("M2M2_MYTHOS_COMMAND", raising=False)
    monkeypatch.delenv("M2M2_MYTHOS_MODEL", raising=False)
    monkeypatch.delenv("FUGU_MODEL", raising=False)

    config = RuntimeConfig.from_env()

    assert config.mythos_command == "fugu-api"
    assert config.mythos_model == "fugu-ultra"


def test_runtime_config_reads_fugu_model_alias(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("M2M2_MYTHOS_MODEL", raising=False)
    monkeypatch.setenv("FUGU_MODEL", "fugu-custom")

    config = RuntimeConfig.from_env()

    assert config.mythos_model == "fugu-custom"
