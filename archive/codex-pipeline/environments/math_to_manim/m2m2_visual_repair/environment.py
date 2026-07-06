"""Prime Intellect Verifiers environment for Math-To-Manim repair tasks."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional, Sequence

from datasets import Dataset
import verifiers as vf
from verifiers.envs.singleturn_env import SingleTurnEnv
from verifiers.parsers.parser import Parser
from verifiers.rubrics.rubric import Rubric
from verifiers.types import Messages

from .scoring import ScoreResult, score_completion


logger = logging.getLogger(__name__)

PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = PACKAGE_ROOT / "data" / "repair_tasks.jsonl"
MAX_PROMPT_CHARS = 2400
DEFAULT_SYSTEM_PROMPT = (
    "You are a Math-To-Manim repair specialist. Repair generated Manim code from typed M2M2 "
    "artifacts. Preserve the requested scene name and educational intent. Return exactly one "
    "<generated_code> block containing JSON. Never access the network, shell out, or read local files."
)


def load_environment(
    dataset_path: str | Path | None = None,
    eval_path: str | Path | None = None,
    max_examples: int = -1,
    eval_examples: int = -1,
    eval_fraction: float = 0.1,
    system_prompt: str | None = None,
    sampling_args: Optional[dict[str, Any]] = None,
    seed: Optional[int] = None,
    task_filter: Optional[Sequence[str]] = None,
) -> vf.Environment:
    """Load the Math-To-Manim visual repair environment."""

    train_records = _prepare_records(_load_jsonl(Path(dataset_path).expanduser() if dataset_path else DEFAULT_DATASET), task_filter)
    if max_examples > 0:
        train_records = train_records[:max_examples]
    if not train_records:
        raise ValueError("No Math-To-Manim repair tasks found.")

    train_dataset = Dataset.from_list(train_records)
    eval_dataset = None
    if eval_path:
        eval_records = _prepare_records(_load_jsonl(Path(eval_path).expanduser()), task_filter)
        if eval_examples > 0:
            eval_records = eval_records[:eval_examples]
        eval_dataset = Dataset.from_list(eval_records) if eval_records else None
    elif eval_fraction > 0 and len(train_dataset) > 1:
        split = train_dataset.train_test_split(test_size=eval_fraction, seed=seed or 42)
        train_dataset = split["train"]
        eval_dataset = split["test"]
        if eval_examples > 0:
            eval_dataset = eval_dataset.select(range(min(eval_examples, len(eval_dataset))))

    rubric = M2M2RepairRubric()
    env = M2M2RepairEnv(
        dataset=train_dataset,
        eval_dataset=eval_dataset,
        system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
        rubric=rubric,
        sampling_args=sampling_args,
    )
    logger.info("Loaded Math-To-Manim repair environment with %d train examples.", len(env.dataset))
    return env


class M2M2RepairParser(Parser):
    """Parser that preserves completion text for generated-code JSON extraction."""

    def parse(self, text: str) -> str:
        return text.strip()

    def parse_answer(self, completion: Messages) -> str:
        parsed = super().parse_answer(completion) or ""
        return parsed.strip()


class M2M2RepairRubric(Rubric):
    """Rubric with fast static rewards for generated Manim repairs."""

    def __init__(self, parser: Parser | None = None):
        parser = parser or M2M2RepairParser()
        funcs = [
            self.format_reward,
            self.schema_reward,
            self.python_parse_reward,
            self.static_validation_reward,
            self.safety_reward,
            self.acceptance_terms_reward,
            self.layout_static_reward,
        ]
        weights = [0.08, 0.12, 0.12, 0.22, 0.13, 0.15, 0.18]
        super().__init__(funcs=funcs, weights=weights, parser=parser)
        self._last_result: ScoreResult | None = None

    def score(self, completion: Messages, answer: str, info: Optional[dict[str, Any]] = None, **_: Any) -> float:
        task = _task_from_answer(answer)
        prediction = self.parser.parse_answer(completion) or ""
        result = score_completion(task, prediction)
        self._last_result = result
        return float(result.score)

    def format_reward(self, completion: Messages, answer: str, parser: Parser, **_: Any) -> float:
        return self._component(completion, answer, parser, "format")

    def schema_reward(self, completion: Messages, answer: str, parser: Parser, **_: Any) -> float:
        return self._component(completion, answer, parser, "schema")

    def python_parse_reward(self, completion: Messages, answer: str, parser: Parser, **_: Any) -> float:
        return self._component(completion, answer, parser, "python_parse")

    def static_validation_reward(self, completion: Messages, answer: str, parser: Parser, **_: Any) -> float:
        return self._component(completion, answer, parser, "static_validation")

    def safety_reward(self, completion: Messages, answer: str, parser: Parser, **_: Any) -> float:
        return self._component(completion, answer, parser, "safety")

    def acceptance_terms_reward(self, completion: Messages, answer: str, parser: Parser, **_: Any) -> float:
        return self._component(completion, answer, parser, "acceptance_terms")

    def layout_static_reward(self, completion: Messages, answer: str, parser: Parser, **_: Any) -> float:
        return self._component(completion, answer, parser, "layout_static")

    def get_last_ledger(self) -> dict[str, Any] | None:
        if self._last_result is None:
            return None
        return {
            "reward_scalar": self._last_result.score,
            **{f"{key}_reward": value for key, value in self._last_result.components.items()},
            "errors": self._last_result.errors,
            "scene_classes": self._last_result.scene_classes,
        }

    def _component(self, completion: Messages, answer: str, parser: Parser, key: str) -> float:
        task = _task_from_answer(answer)
        prediction = parser.parse_answer(completion) or ""
        result = score_completion(task, prediction)
        return float(result.components.get(key, 0.0))


class M2M2RepairEnv(SingleTurnEnv):
    """Single-turn repair environment."""

    def __init__(
        self,
        dataset: Dataset,
        eval_dataset: Optional[Dataset],
        system_prompt: str,
        rubric: M2M2RepairRubric,
        sampling_args: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ):
        super().__init__(
            dataset=dataset,
            eval_dataset=eval_dataset,
            system_prompt=system_prompt,
            parser=rubric.parser,
            rubric=rubric,
            sampling_args=sampling_args,
            message_type="chat",
            **kwargs,
        )
        self.rubric = rubric

    def get_reward_ledger(self) -> dict[str, Any] | None:
        return self.rubric.get_last_ledger()


def _prepare_records(entries: list[dict[str, Any]], task_filter: Optional[Sequence[str]] = None) -> list[dict[str, Any]]:
    allowed = {item.lower() for item in task_filter or []}
    records = []
    for index, task in enumerate(entries):
        task_type = str(task.get("task_type") or "manim_repair")
        if allowed and task_type.lower() not in allowed:
            continue
        task_id = str(task.get("task_id") or f"m2m2_repair_{index:05d}")
        prompt = _build_question(task)
        records.append(
            {
                "id": task_id,
                "question": prompt,
                "answer": json.dumps(task, sort_keys=True),
                "task": task_type,
                "info": {
                    "task_id": task_id,
                    "scene_name": task.get("scene_name"),
                    "acceptance_terms": task.get("acceptance_terms") or [],
                },
            }
        )
    return records


def _build_question(task: dict[str, Any]) -> str:
    payload = {
        "prompt": _truncate(task.get("prompt"), MAX_PROMPT_CHARS),
        "audience": task.get("audience"),
        "style": task.get("style"),
        "duration_seconds": task.get("duration_seconds"),
        "scene_name": task.get("scene_name"),
        "acceptance_terms": task.get("acceptance_terms") or [],
        "scene_spec": _compact_scene_spec(task.get("scene_spec")),
        "current_generated_code": _compact_generated_code(task.get("generated_code")),
        "evidence": task.get("evidence"),
        "layout_objectives": task.get("layout_objectives") or [],
        "instructions": task.get("instructions"),
    }
    return (
        "Repair this Math-To-Manim generated Manim scene.\n\n"
        f"{json.dumps(payload, indent=2, sort_keys=True)}\n\n"
        "Return exactly:\n"
        "<generated_code>{...GeneratedCode JSON...}</generated_code>\n"
    )


def _compact_scene_spec(scene_spec: Any) -> Any:
    if not isinstance(scene_spec, dict):
        return scene_spec
    compact = {
        "scene_name": scene_spec.get("scene_name"),
        "camera": scene_spec.get("camera"),
        "config": scene_spec.get("config"),
        "code_requirements": scene_spec.get("code_requirements") or [],
        "objects": scene_spec.get("objects") or [],
        "animations": scene_spec.get("animations") or [],
    }
    metadata = scene_spec.get("metadata") if isinstance(scene_spec.get("metadata"), dict) else {}
    compact["metadata"] = {
        "requested_style": metadata.get("requested_style"),
        "requested_duration_seconds": metadata.get("requested_duration_seconds"),
    }
    return compact


def _compact_generated_code(generated_code: Any) -> Any:
    if not isinstance(generated_code, dict):
        return generated_code
    return {
        "scene_name": generated_code.get("scene_name"),
        "language": generated_code.get("language"),
        "code": generated_code.get("code"),
        "dependencies": generated_code.get("dependencies") or [],
        "manim_version": generated_code.get("manim_version"),
        "source_spec_id": generated_code.get("source_spec_id"),
        "metadata": {
            "notes": (generated_code.get("metadata") or {}).get("notes")
            if isinstance(generated_code.get("metadata"), dict)
            else None
        },
    }


def _truncate(value: Any, max_chars: int) -> Any:
    if not isinstance(value, str) or len(value) <= max_chars:
        return value
    return value[:max_chars].rstrip() + "\n...[truncated for repair prompt]"


def _task_from_answer(answer: str) -> dict[str, Any]:
    try:
        payload = json.loads(answer)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                logger.warning("Skipping malformed JSON on line %d of %s: %s", line_no, path, exc)
                continue
            if isinstance(payload, dict):
                entries.append(payload)
    return entries
