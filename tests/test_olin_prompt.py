from pathlib import Path


PROMPT = Path("docs/prompts/olin-off-white-3d-space.md")


def test_olin_prompt_targets_mythos_and_has_all_hard_contracts():
    text = PROMPT.read_text(encoding="utf-8")

    required = (
        "Claude Fable 5 Mythos",
        "Claude Code CLI",
        "createCanvas(w=400,w)",
        r"k=\bigl(4+\cos(i/9-2t)\bigr)\cos(i/35)",
        r"d=\sqrt{k^2+e^2}",
        r"c=d-t",
        r"q=2\sin(3k)",
        r"(40+q)\cos c",
        r"35\,d",
        "#f3ecd8",
        "#241a12",
        "ThreeDScene",
        "true 3D",
        "move_camera()",
        "complete valid LaTeX",
        "Do not use a starfield",
        "PMobject",
        "6000 points",
    )
    for item in required:
        assert item in text, item

    assert "Sol" not in text
    assert "codex" not in text.lower()
