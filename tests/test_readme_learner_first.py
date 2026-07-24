import re
from pathlib import Path


README = Path("README.md")

FEATURED_EXPLAINERS = [
    "docs/showcase/assets/erdos-1038-potential-landscape.gif",
    "docs/showcase/assets/jacobian-conjecture-3d.gif",
    "docs/showcase/assets/traitor-axis.gif",
    "docs/showcase/assets/vortex-leapfrog.gif",
    "docs/showcase/assets/the-valley.gif",
    "docs/showcase/assets/exceptional-point-monodromy.gif",
]


def readme_text() -> str:
    return README.read_text(encoding="utf-8")


def local_gif_references(text: str) -> list[str]:
    return re.findall(r'docs/showcase/assets/[^"\']+\.gif', text)


def test_featured_explainers_are_first_and_in_order():
    text = readme_text()
    references = local_gif_references(text)

    assert references[:6] == FEATURED_EXPLAINERS
    assert "api.star-history.com/chart" in text
    assert "Ask a question. Get a visual explainer." in text
    assert "docs/showcase/README.md" in text


def test_every_featured_explainer_asset_exists():
    for asset in FEATURED_EXPLAINERS:
        assert Path(asset).is_file()


def test_product_definition_and_manim_credit_are_present():
    text = readme_text()

    assert "## What Is Math To Manim" in text
    assert "carefully reasoned visual explanation" in text
    assert "originally created by Grant Sanderson for 3Blue1Brown" in text
    assert "https://docs.manim.community/en/stable/" in text


def test_prompt_examples_cover_beginner_through_research_levels():
    text = readme_text()

    required_phrases = [
        "eighth grade student",
        "Pythagorean theorem",
        "Teach slope using three ramps",
        "conservation of momentum",
        "Fourier series as rotating vectors",
        "exceptional point swaps the eigenvalue branches",
        "Assume they already know",
        "End with",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_reasoning_flow_uses_learning_order():
    text = readme_text()
    stages = [
        "Understand the learner",
        "Find the missing prerequisites",
        "Build the teaching sequence",
        "Choose the mathematics",
        "Plan the visuals",
        "Compose the Manim scene",
        "Validate the result",
        "Render, inspect, and repair",
    ]

    positions = [text.index(stage) for stage in stages]
    assert positions == sorted(positions)
