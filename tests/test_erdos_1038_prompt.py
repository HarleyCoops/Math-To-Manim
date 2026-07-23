from pathlib import Path


PROMPT = Path("docs/prompts/erdos-1038-off-white-3d.md")


def test_erdos_1038_prompt_targets_sol_and_has_all_hard_contracts():
    text = PROMPT.read_text(encoding="utf-8")

    required = (
        "GPT-5.6 Sol",
        "Erdős Problem 1038",
        r"V_{\mu_f}(x)",
        r"E_{\widetilde\mu}\subseteq E_\mu",
        r"\Lambda(q)",
        "1.834430475762661",
        r"2\sqrt{2}",
        r"(x^2-1)^m",
        "#f3ecd8",
        "#241a12",
        "ThreeDScene",
        "true 3D",
        "move_camera()",
        "complete valid LaTeX",
        "Do not use a starfield",
        "outward interval arithmetic",
        "not attained",
    )
    for item in required:
        assert item in text, item

    assert "Mythos" not in text
    assert "math-to-manim " not in text
