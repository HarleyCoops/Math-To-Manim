from __future__ import annotations

import pytest
from pydantic import ValidationError

from m2m2_visual_improvement.schemas import (
    Diagnosis,
    EditableBaseline,
    EducationalContract,
    MetricScore,
    OcrBox,
    Resolution,
    RewardLedger,
    RevisionScope,
    VisualEvidence,
    VisualRevision,
)


SHA = "a" * 64
BASELINE_CODE = "from manim import *\nclass Lesson(Scene):\n    def construct(self):\n        pass\n"


def contract_payload() -> dict:
    return {
        "task_id": "synthetic.scene_01.off_frame.00",
        "source_id": "scene_01",
        "original_request": "Explain why two negatives multiply to a positive.",
        "audience": "grade 8",
        "required_concepts": ["sign", "multiplication"],
        "required_formulas": ["(-2)(-3)=6"],
        "required_narrative_beats": ["show signs", "show result"],
        "min_duration_seconds": 6.0,
        "max_duration_seconds": 12.0,
        "provider": "synthetic",
        "source_artifact_hashes": {"scene.py": SHA},
    }


def baseline() -> EditableBaseline:
    return EditableBaseline(
        scene_spec={"scene_name": "Lesson", "objects": [{"id": "title"}]},
        code=BASELINE_CODE,
        render_manifest={"status": "completed"},
        contact_sheet_sha256=SHA,
        frame_sha256=(SHA,),
        focus_beats=(),
    )


def evidence() -> VisualEvidence:
    return VisualEvidence(
        render_status="completed",
        duration_seconds=8.0,
        resolution=Resolution(width=854, height=480),
        sampled_timestamps=(0.0, 4.0, 8.0),
        contact_sheet_sha256=SHA,
        frame_sha256=(SHA,),
        ocr_boxes=(
            OcrBox(
                text="(-2)(-3)=6",
                confidence=0.99,
                x=100,
                y=100,
                width=200,
                height=40,
                timestamp=4.0,
            ),
        ),
        tracked_objects=(),
        focus_measurements=(),
        clipping_ratio=0.0,
        overlap_ratio=0.0,
        density_ratio=0.2,
    )


def valid_revision(**updates: object) -> VisualRevision:
    payload: dict[str, object] = {
        "schema_version": "m2m2.visual_revision.v1",
        "scope": "code_only",
        "diagnosis": [
            {
                "category": "crowding",
                "evidence": "The equation overlaps the caption.",
                "intent": "Stage the equation after the caption.",
            }
        ],
        "scene_spec_patch": None,
        "code": BASELINE_CODE,
        "expected_improvements": ["legibility"],
    }
    payload.update(updates)
    return VisualRevision.model_validate(
        payload,
        context={"baseline_code": BASELINE_CODE},
    )


def metric(name: str) -> MetricScore:
    return MetricScore(
        name=name,
        baseline=0.4,
        candidate=0.7,
        relative=0.65,
        raw={"violations": 0},
    )


def ledger_payload() -> dict:
    return {
        "schema_version": "m2m2.reward_ledger.v1",
        "task_id": "synthetic.scene_01.off_frame.00",
        "eligible": True,
        "exclusion": None,
        "raw_measurements": {"required_token_coverage": 1.0},
        "component_scores": {
            "framing": metric("framing"),
            "legibility": metric("legibility"),
            "focus": metric("focus"),
            "pairwise_visual_preference": metric("pairwise_visual_preference"),
        },
        "judge_orders": ("candidate_baseline", "baseline_candidate"),
        "judge_verdicts": ("win", "win"),
        "judge_order_consistent": True,
        "aggregate_reward": 0.65,
        "runtime_image_digest": SHA,
        "environment_sha256": SHA,
        "dataset_sha256": SHA,
        "config_sha256": SHA,
        "judge_prompt_sha256": SHA,
        "model_id": "Qwen/Qwen3-VL-4B-Instruct",
        "judge_model_id": "vision-judge",
        "timing_seconds": {"render": 1.2, "judge": 0.4},
    }


def test_code_only_rejects_scene_spec_patch() -> None:
    with pytest.raises(ValidationError, match="code_only"):
        valid_revision(scene_spec_patch={"objects": []})


def test_hierarchical_requires_scene_spec_patch() -> None:
    with pytest.raises(ValidationError, match="spec_and_code"):
        valid_revision(scope=RevisionScope.SPEC_AND_CODE)


def test_no_change_requires_baseline_code_and_diagnosis() -> None:
    payload = {
        "schema_version": "m2m2.visual_revision.v1",
        "scope": "no_change",
        "diagnosis": [],
        "scene_spec_patch": None,
        "code": "different",
        "expected_improvements": [],
    }
    with pytest.raises(ValidationError, match="diagnosis"):
        VisualRevision.model_validate(
            payload,
            context={"baseline_code": BASELINE_CODE},
        )

    payload["diagnosis"] = [
        {
            "category": "none",
            "evidence": "All visual checks are already satisfied.",
            "intent": "Preserve the baseline.",
        }
    ]
    with pytest.raises(ValidationError, match="baseline code"):
        VisualRevision.model_validate(
            payload,
            context={"baseline_code": BASELINE_CODE},
        )

    payload["code"] = BASELINE_CODE
    assert (
        VisualRevision.model_validate(
            payload,
            context={"baseline_code": BASELINE_CODE},
        ).scope
        is RevisionScope.NO_CHANGE
    )


def test_contract_rejects_empty_required_concepts() -> None:
    payload = contract_payload()
    payload["required_concepts"] = []
    with pytest.raises(ValidationError):
        EducationalContract.model_validate(payload)


def test_evidence_hashes_are_sha256() -> None:
    assert evidence().contact_sheet_sha256 == SHA
    payload = evidence().model_dump()
    payload["contact_sheet_sha256"] = "not-a-hash"
    with pytest.raises(ValidationError):
        VisualEvidence.model_validate(payload)


def test_reward_ledger_requires_every_component_and_digest() -> None:
    payload = ledger_payload()
    payload["component_scores"].pop("focus")
    with pytest.raises(ValidationError, match="focus"):
        RewardLedger.model_validate(payload)

    payload = ledger_payload()
    payload.pop("dataset_sha256")
    with pytest.raises(ValidationError):
        RewardLedger.model_validate(payload)


def test_secrets_cannot_serialize_into_ledger() -> None:
    payload = ledger_payload()
    payload["raw_measurements"] = {
        "nested": {"authorization": "Bearer should-never-be-here"}
    }
    with pytest.raises(ValidationError, match="secret-like"):
        RewardLedger.model_validate(payload)

    assert "api_key" not in RewardLedger.model_validate(
        ledger_payload()
    ).model_dump_json()


def test_models_are_frozen_and_reject_unknown_fields() -> None:
    contract = EducationalContract.model_validate(contract_payload())
    with pytest.raises(ValidationError):
        EducationalContract.model_validate(
            {**contract_payload(), "unknown": "value"}
        )
    with pytest.raises(ValidationError):
        contract.task_id = "changed"


def test_baseline_and_diagnosis_are_typed() -> None:
    assert baseline().scene_spec["scene_name"] == "Lesson"
    assert isinstance(valid_revision().diagnosis[0], Diagnosis)
