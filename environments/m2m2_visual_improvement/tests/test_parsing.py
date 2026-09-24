import json

import pytest

from m2m2_visual_improvement.parsing import (
    VisualRevisionParseError,
    parse_visual_revision,
)
from m2m2_visual_improvement.schemas import RevisionScope


BASELINE_CODE = "from manim import *\nclass Lesson(Scene):\n    def construct(self):\n        pass\n"


def valid_payload() -> dict:
    return {
        "schema_version": "m2m2.visual_revision.v1",
        "scope": "code_only",
        "diagnosis": [
            {
                "category": "crowding",
                "evidence": "The caption overlaps the formula.",
                "intent": "Stage them sequentially.",
            }
        ],
        "scene_spec_patch": None,
        "code": BASELINE_CODE,
        "expected_improvements": ["legibility"],
    }


def tagged(payload: dict) -> str:
    return (
        "<visual_revision>"
        + json.dumps(payload, separators=(",", ":"))
        + "</visual_revision>"
    )


def test_parses_exactly_one_tagged_revision() -> None:
    revision = parse_visual_revision(
        tagged(valid_payload()),
        baseline_code=BASELINE_CODE,
    )
    assert revision.scope is RevisionScope.CODE_ONLY
    assert revision.code == BASELINE_CODE


@pytest.mark.parametrize(
    "output",
    [
        "{}",
        "<visual_revision>{}</visual_revision>"
        "<visual_revision>{}</visual_revision>",
        "explanation\n<visual_revision>{}</visual_revision>",
        "<visual_revision>{}</visual_revision>\nmore",
    ],
)
def test_rejects_missing_duplicate_or_surrounded_action(output: str) -> None:
    with pytest.raises(VisualRevisionParseError):
        parse_visual_revision(output, baseline_code=BASELINE_CODE)


def test_rejects_invalid_json() -> None:
    with pytest.raises(VisualRevisionParseError, match="JSON"):
        parse_visual_revision(
            "<visual_revision>{not json}</visual_revision>",
            baseline_code=BASELINE_CODE,
        )


def test_rejects_unknown_fields() -> None:
    payload = valid_payload()
    payload["api_key"] = "not-allowed"
    with pytest.raises(VisualRevisionParseError, match="valid VisualRevision"):
        parse_visual_revision(tagged(payload), baseline_code=BASELINE_CODE)


def test_rejects_output_over_byte_limit() -> None:
    with pytest.raises(VisualRevisionParseError, match="byte limit"):
        parse_visual_revision(
            tagged(valid_payload()),
            baseline_code=BASELINE_CODE,
            max_bytes=10,
        )


def test_no_change_is_validated_against_baseline_context() -> None:
    payload = valid_payload()
    payload["scope"] = "no_change"
    payload["code"] = "different"
    with pytest.raises(VisualRevisionParseError, match="baseline code"):
        parse_visual_revision(tagged(payload), baseline_code=BASELINE_CODE)
