"""Unit tests for LLM client interface and JSON parsing."""

import pytest

from src.agents.llm_client import parse_json_response, LLMClient, create_client


class TestParseJsonResponse:
    """Tests for the JSON response parser."""

    def test_parse_plain_array(self):
        result = parse_json_response('["a", "b", "c"]')
        assert result == ["a", "b", "c"]

    def test_parse_plain_object(self):
        result = parse_json_response('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_from_code_fence(self):
        text = 'Here are the results:\n```json\n["x", "y"]\n```\n'
        result = parse_json_response(text)
        assert result == ["x", "y"]

    def test_parse_from_code_fence_no_lang(self):
        text = '```\n["x", "y"]\n```'
        result = parse_json_response(text)
        assert result == ["x", "y"]

    def test_parse_array_from_noisy_text(self):
        text = 'The prerequisites are: ["calculus", "linear algebra"] and more.'
        result = parse_json_response(text)
        assert result == ["calculus", "linear algebra"]

    def test_parse_object_from_noisy_text(self):
        text = 'Analysis: {"core_concept": "QFT", "level": "advanced"} done.'
        result = parse_json_response(text)
        assert result == {"core_concept": "QFT", "level": "advanced"}

    def test_raises_on_unparseable(self):
        with pytest.raises(ValueError, match="Could not parse JSON"):
            parse_json_response("This is just plain text with no JSON.")

    def test_whitespace_handling(self):
        result = parse_json_response('  \n  ["a"]  \n  ')
        assert result == ["a"]


class MockLLMClient(LLMClient):
    """A mock LLM client for testing."""

    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self._call_count = 0

    def query(self, user_prompt, system_prompt="", max_tokens=500, temperature=0.3):
        idx = min(self._call_count, len(self._responses) - 1)
        self._call_count += 1
        return self._responses[idx]

    @property
    def model_name(self):
        return "mock-model"


class TestCreateClient:
    """Tests for the client factory."""

    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="Unknown backend"):
            create_client("nonexistent")

    def test_anthropic_requires_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            create_client("anthropic")

    def test_deepseek_requires_key(self, monkeypatch):
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
            create_client("deepseek")

    def test_kimi_requires_key(self, monkeypatch):
        monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="MOONSHOT_API_KEY"):
            create_client("kimi")
