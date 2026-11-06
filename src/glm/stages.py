"""The GLM stage table: the single source of stage order, charters and behaviour.

Each stage names its charter file, the artifact it writes, the server-side
abilities its prompt may mention (advisory only; they never reach the wire),
the local function tools it may call, and the harness hooks that differ per
stage. Adding or reordering a stage happens here and nowhere else: the run
bundle contract, the prompts and the traces all derive from ``STAGES``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from glm.client import FunctionTool
from glm.models import REVIEW_FILE, SCENE_FILE, VALIDATION_FILE
from glm.tools import VERIFY_SCENE
from glm.validation import normalize_reverse_tree, validate_reverse_tree

PACKAGE_DIR = Path(__file__).resolve().parent
AGENT_DIR = PACKAGE_DIR / "agents"

WEB_SEARCH = "web_search"
CODE_INTERPRETER = "code_interpreter"


@dataclass(frozen=True)
class Stage:
    name: str
    charter_file: str
    artifact: str
    # Platform abilities named in the prompt as something the stage may lean on
    # conceptually. Runs stay reproducible from artifacts alone, so these are
    # never sent as tools.
    advisories: tuple[str, ...] = ()
    # Local functions the model may call; each schema carries its handler.
    tools: tuple[FunctionTool, ...] = ()
    # The user's attached image goes to this stage only.
    takes_image: bool = False
    # Coerce the stage's JSON into its contract before saving it.
    normalize: Callable[[dict], dict] | None = None
    # Contract failures that end the run at this stage (list of messages).
    check: Callable[[dict], list[str]] | None = None
    # This stage must also hand back the complete scene source.
    writes_scene: bool = False

    @property
    def tools_requested(self) -> list[str]:
        """What a trace records as requested: real tools, then advisories."""
        return [tool.name for tool in self.tools] + list(self.advisories)

    def charter(self) -> str:
        path = AGENT_DIR / self.charter_file
        if not path.is_file():
            raise FileNotFoundError(f"missing GLM charter: {path}")
        return path.read_text(encoding="utf-8")


STAGES: tuple[Stage, ...] = (
    Stage("intent", "glm-intent.md", "01_intent.json", takes_image=True),
    Stage(
        "cartographer",
        "glm-cartographer.md",
        "02_knowledge_map.json",
        advisories=(WEB_SEARCH,),
        normalize=normalize_reverse_tree,
        check=validate_reverse_tree,
    ),
    Stage("curriculum", "glm-curriculum.md", "03_curriculum.json"),
    Stage(
        "math-director",
        "glm-math-director.md",
        "04_math_dossier.json",
        advisories=(CODE_INTERPRETER, WEB_SEARCH),
    ),
    Stage(
        "cinematographer",
        "glm-cinematographer.md",
        "05_shot_list.json",
        advisories=(WEB_SEARCH,),
    ),
    Stage(
        "composer",
        "glm-composer.md",
        "06_scene_spec.json",
        tools=(VERIFY_SCENE,),
        writes_scene=True,
    ),
)

SCENE_STAGE = next(stage for stage in STAGES if stage.writes_scene)

# Every file a completed run bundle must contain, in bundle order.
BUNDLE_FILES: tuple[str, ...] = tuple(stage.artifact for stage in STAGES) + (
    SCENE_FILE,
    VALIDATION_FILE,
    REVIEW_FILE,
)


def stage_prompt(stage: Stage, prompt: str, prior: dict[str, dict]) -> str:
    """User turn for one stage; platform-only abilities become advisories."""
    dossier = json.dumps(prior, indent=2) if prior else "{}"
    advisory = ""
    if stage.advisories:
        advisory = (
            f"Platform abilities this stage may reference conceptually: "
            f"{', '.join(stage.advisories)}. Output stays plain text/JSON.\n"
        )
    return (
        f"User request:\n{prompt}\n\n"
        f"You are the {stage.name} stage of the GLM chain. Thinking is on.\n"
        "Return one JSON object with exactly the keys the charter names.\n"
        "If you write the scene, also include a source field with the complete "
        "Python file, or a fenced python block.\n"
        f"{advisory}\n"
        f"Upstream artifacts:\n{dossier}\n"
    )
