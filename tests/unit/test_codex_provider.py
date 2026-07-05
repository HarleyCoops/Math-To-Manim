from __future__ import annotations

import json
import subprocess

import pytest

from math_to_manim.config import RuntimeConfig
from math_to_manim.schemas import GeneratedCode, ManimSceneSpec


class FakeRunner:
    def __init__(self, payload: dict[str, object]):
        self.payload = payload
        self.calls: list[list[str]] = []
        self.kwargs: list[dict[str, object]] = []

    def __call__(self, cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append(cmd)
        self.kwargs.append(kwargs)
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
    assert runner.calls == [["codex", "exec", "--full-auto", "--model", "gpt-5.5", "-"]]
    assert "Return only valid JSON" in runner.kwargs[0]["input"]
    assert "DemoScene" in runner.kwargs[0]["input"]


def test_mythos_harness_can_use_codex_oauth_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    from mythos.harness import MythosHarness

    calls: list[list[str]] = []
    kwargs_seen: list[dict[str, object]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        kwargs_seen.append(kwargs)
        return subprocess.CompletedProcess(cmd, 0, stdout='{"ok": true}', stderr="")

    monkeypatch.setattr("mythos.harness.subprocess.run", fake_run)
    monkeypatch.setattr("mythos.harness._resolve_command", lambda command: command)
    harness = MythosHarness(command="codex", model="gpt-5.5")

    output = harness._model("Return JSON only.")

    assert output == '{"ok": true}'
    assert calls == [["codex", "exec", "--model", "gpt-5.5", "-"]]
    assert kwargs_seen[0]["input"] == "Return JSON only."


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
    monkeypatch.setenv("M2M2_MANIM_COMMAND", "python -m manim")

    config = RuntimeConfig.from_env()

    assert config.codegen_provider == "codex-cli"
    assert config.codex_command == "codex-custom"
    assert config.codex_full_auto is True
    assert config.codex_timeout_seconds == 123
    assert config.manim_command == ("python", "-m", "manim")


def test_codex_command_resolution_prefers_windows_cmd_shim(monkeypatch: pytest.MonkeyPatch) -> None:
    from math_to_manim.providers import codex_cli

    monkeypatch.setattr(codex_cli.os, "name", "nt")
    monkeypatch.setattr(codex_cli.shutil, "which", lambda command: "C:/npm/codex.cmd" if command == "codex.cmd" else None)

    assert codex_cli._resolve_codex_command("codex") == "C:/npm/codex.cmd"


def test_mythos_provider_routes_fugu_api_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    from math_to_manim.providers.mythos_cli import MythosCliProvider

    payload = {
        "scene_name": "DemoScene",
        "code": "from manim import *\nclass DemoScene(ThreeDScene):\n    def construct(self):\n        self.wait()\n",
        "dependencies": ["manim"],
        "metadata": {"note": "from fake fugu"},
    }
    calls: list[dict[str, object]] = []

    def fake_call(prompt: str, **kwargs: object) -> str:
        calls.append({"prompt": prompt, **kwargs})
        return json.dumps(payload)

    monkeypatch.setattr("math_to_manim.providers.mythos_cli.call_fugu_chat", fake_call)
    monkeypatch.setattr("math_to_manim.providers.mythos_cli.fugu_base_url_from_env", lambda: "https://example.test/v1")
    provider = MythosCliProvider(
        config=RuntimeConfig(
            codegen_provider="fugu-api",
            mythos_command="fugu-api",
            mythos_model="fugu-ultra",
        )
    )

    generated = provider.generate_code(ManimSceneSpec(scene_name="DemoScene"))

    assert generated.scene_name == "DemoScene"
    assert generated.metadata["runtime"] == "fugu_api"
    assert generated.metadata["provider"] == "mythos-fugu-api"
    assert generated.metadata["model"] == "fugu-ultra"
    assert calls[0]["model"] == "fugu-ultra"
    assert calls[0]["base_url"] == "https://example.test/v1"
    assert "Mythos" in calls[0]["prompt"]


def test_manim_code_agent_routes_codegen_to_fugu_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    from math_to_manim.agents.codegen import ManimCodeAgent

    class StubProvider:
        def __init__(self, config: RuntimeConfig):
            self.config = config

        def generate_code(self, spec: ManimSceneSpec) -> GeneratedCode:
            return GeneratedCode(
                scene_name=spec.scene_name,
                code="from manim import *\nclass DemoScene(ThreeDScene):\n    def construct(self):\n        self.wait()\n",
                dependencies=["manim"],
                metadata={"runtime": "fugu_api", "file_path": "generated_scene.py"},
            )

    monkeypatch.setattr("math_to_manim.agents.codegen.MythosCliProvider", StubProvider)
    agent = ManimCodeAgent(RuntimeConfig(codegen_provider="fugu-api"))

    generated = agent.run(ManimSceneSpec(scene_name="DemoScene"))

    assert generated.metadata["runtime"] == "fugu_api"
