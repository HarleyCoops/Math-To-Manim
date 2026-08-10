from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import os
from pathlib import Path
import sys
import types as stdlib_types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
OPENAI_BASE = ROOT / "archive/codex-pipeline/math_to_manim/agents/base.py"
OPENAI_PACKAGE = ROOT / "archive/codex-pipeline"
GEMINI_AGENTS = ROOT / "legacy/Math-To-Manim/Gemini3/src/agents.py"
GEMINI_PIPELINE = ROOT / "legacy/Math-To-Manim/Gemini3/src/pipeline.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class AgentSecurityConfigurationTests(unittest.TestCase):
    def test_openai_sdk_runs_disable_tracing(self):
        calls = []

        class Agent:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        @dataclass
        class RunConfig:
            tracing_disabled: bool = False

        class Runner:
            @classmethod
            def run_sync(cls, agent, prompt, *, run_config):
                calls.append(run_config)
                return stdlib_types.SimpleNamespace(final_output={"ok": True})

        agents = stdlib_types.ModuleType("agents")
        agents.Agent = Agent
        agents.RunConfig = RunConfig
        agents.Runner = Runner
        agents.function_tool = object()
        agents.handoff = object()

        agent_output = stdlib_types.ModuleType("agents.agent_output")

        class AgentOutputSchema:
            def __init__(self, output_type, strict_json_schema):
                self.output_type = output_type
                self.strict_json_schema = strict_json_schema

        agent_output.AgentOutputSchema = AgentOutputSchema

        modules = {
            "agents": agents,
            "agents.agent_output": agent_output,
        }
        sys.path.insert(0, str(OPENAI_PACKAGE))
        try:
            with patch.dict(sys.modules, modules), patch.dict(
                os.environ, {"OPENAI_API_KEY": "test-key"}
            ):
                module = _load_module("security_test_openai_base", OPENAI_BASE)

                self.assertEqual(
                    module.maybe_run_sdk_agent(
                        name="test",
                        instructions="test",
                        prompt="test",
                        model="test-model",
                        output_parser=lambda output: output,
                    ),
                    '{"ok": true}',
                )

                class Output:
                    @classmethod
                    def model_validate(cls, value):
                        return value

                self.assertEqual(
                    module.run_structured_sdk_agent(
                        name="test",
                        instructions="test",
                        prompt="test",
                        model="test-model",
                        output_type=Output,
                    ),
                    {"ok": True},
                )
        finally:
            sys.path.remove(str(OPENAI_PACKAGE))
            sys.modules.pop("security_test_openai_base", None)

        self.assertEqual(len(calls), 2)
        self.assertTrue(
            all(run_config.tracing_disabled is True for run_config in calls)
        )

    def test_gemini_agents_have_descriptions_and_explicit_safety(self):
        google = stdlib_types.ModuleType("google")
        google.__path__ = []
        adk = stdlib_types.ModuleType("google.adk")
        adk.__path__ = []
        adk_agents = stdlib_types.ModuleType("google.adk.agents")
        genai = stdlib_types.ModuleType("google.genai")
        genai.__path__ = []
        genai_types = stdlib_types.ModuleType("google.genai.types")

        class Agent:
            def __init__(self, **kwargs):
                vars(self).update(kwargs)

        class SafetySetting:
            def __init__(self, *, category, threshold):
                self.category = category
                self.threshold = threshold

        class GenerateContentConfig:
            def __init__(self, **kwargs):
                vars(self).update(kwargs)

        adk_agents.Agent = Agent
        genai_types.SafetySetting = SafetySetting
        genai_types.GenerateContentConfig = GenerateContentConfig
        genai_types.HarmCategory = stdlib_types.SimpleNamespace(
            HARM_CATEGORY_HARASSMENT="harassment",
            HARM_CATEGORY_HATE_SPEECH="hate_speech",
            HARM_CATEGORY_SEXUALLY_EXPLICIT="sexually_explicit",
            HARM_CATEGORY_DANGEROUS_CONTENT="dangerous_content",
        )
        genai_types.HarmBlockThreshold = stdlib_types.SimpleNamespace(
            BLOCK_MEDIUM_AND_ABOVE="block_medium_and_above",
        )
        genai.types = genai_types

        package = stdlib_types.ModuleType("security_test_gemini")
        package.__path__ = [str(GEMINI_AGENTS.parent)]
        core = stdlib_types.ModuleType("security_test_gemini.core")
        core.get_model_config = lambda: {"model": "test-model"}

        modules = {
            "google": google,
            "google.adk": adk,
            "google.adk.agents": adk_agents,
            "google.genai": genai,
            "google.genai.types": genai_types,
            "security_test_gemini": package,
            "security_test_gemini.core": core,
        }
        with patch.dict(sys.modules, modules):
            module = _load_module("security_test_gemini.agents", GEMINI_AGENTS)
            factories = (
                module.create_concept_analyzer,
                module.create_prerequisite_explorer,
                module.create_mathematical_enricher,
                module.create_visual_designer,
                module.create_narrative_composer,
                module.create_code_generator,
            )
            agents = [factory() for factory in factories]

        self.assertTrue(all(agent.description.strip() for agent in agents))
        self.assertEqual(
            len({id(agent.generate_content_config) for agent in agents}), len(agents)
        )
        expected_categories = set(module.SAFETY_CATEGORIES)
        for agent in agents:
            settings = agent.generate_content_config.safety_settings
            self.assertEqual(
                {setting.category for setting in settings}, expected_categories
            )
            self.assertTrue(
                all(
                    setting.threshold
                    == genai_types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                    for setting in settings
                )
            )
        sys.modules.pop("security_test_gemini.agents", None)

    def test_direct_gemini_client_reuses_the_safe_config(self):
        source = GEMINI_PIPELINE.read_text(encoding="utf-8")

        self.assertIn("config=create_safe_generate_content_config(", source)
        self.assertIn("system_instruction=agent.instruction", source)
        self.assertNotIn('config={\n                "system_instruction"', source)


if __name__ == "__main__":
    unittest.main()
