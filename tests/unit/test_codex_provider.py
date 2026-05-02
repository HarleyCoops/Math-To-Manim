from __future__ import annotations

import json
import subprocess
from unittest.mock import ANY

import pytest

from math_to_manim.config import RuntimeConfig
from math_to_manim.schemas import GeneratedCode, ManimSceneSpec


class FakeRunner:
    def __init__(self, payload: dict[str, object]):
        self.payload = payload
        self.calls: list[list[str]] = []

    def __call__(self, cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(self.payload), stderr="")


def test_codex_cli_provider_builds_exec_command_and_parses_generated_code() -> None:
    from math_to_manim.providers.codex_cli import CodexCliProvider

    payload = {
        "scene_name": "DemoScene",
        "code": "from manim import *\nclass DemoScene(Scene):\n    def construct(self):\n        self.wait()\n",
        "dependencies": ["manim"],
        "metadata": {"note": "from fake codex"},
    }
    runner = FakeRunner(payload)
    provider = CodexCliProvider(config=RuntimeConfig(codex_full_auto=True), runner=runner)
    spec = ManimSceneSpec(scene_name="DemoScene", code_requirements=["show a dot"])

    generated = provider.generate_code(spec)

    assert generated.scene_name == "DemoScene"
    assert generated.code.startswith("from manim import *")
    assert generated.metadata["runtime"] == "codex_cli"
    assert generated.metadata["file_path"] == "generated_scene.py"
    assert runner.calls == [["codex", "exec", "--full-auto", ANY]]
    assert "Return only valid JSON" in runner.calls[0][-1]
    assert "DemoScene" in runner.calls[0][-1]


def test_manim_code_agent_routes_codegen_to_codex_provider_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    from math_to_manim.agents.codegen import ManimCodeAgent

    class StubProvider:
        def __init__(self, config: RuntimeConfig):
            self.config = config

        def generate_code(self, spec: ManimSceneSpec) -> GeneratedCode:
            return GeneratedCode(
                scene_name=spec.scene_name,
                code="from manim import *\nclass DemoScene(Scene):\n    def construct(self):\n        self.wait()\n",
                dependencies=["manim"],
                metadata={"runtime": "codex_cli", "file_path": "generated_scene.py"},
            )

    monkeypatch.setattr("math_to_manim.agents.codegen.CodexCliProvider", StubProvider)
    agent = ManimCodeAgent(RuntimeConfig(codegen_provider="codex-cli"))

    generated = agent.run(ManimSceneSpec(scene_name="DemoScene"))

    assert generated.metadata["runtime"] == "codex_cli"


def test_runtime_config_reads_codex_provider_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("M2M2_CODEGEN_PROVIDER", "codex-cli")
    monkeypatch.setenv("M2M2_CODEX_COMMAND", "codex-custom")
    monkeypatch.setenv("M2M2_CODEX_FULL_AUTO", "1")
    monkeypatch.setenv("M2M2_CODEX_TIMEOUT_SECONDS", "123")

    config = RuntimeConfig.from_env()

    assert config.codegen_provider == "codex-cli"
    assert config.codex_command == "codex-custom"
    assert config.codex_full_auto is True
    assert config.codex_timeout_seconds == 123
