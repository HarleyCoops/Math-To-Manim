import re
from pathlib import Path


README = Path("README.md")

FEATURED_EXPLAINERS = [
    "docs/showcase/assets/erdos-1038-potential-landscape.gif",
    "docs/showcase/assets/jacobian-conjecture-3d.gif",
]

REMOVED_MYTHOS_SHOWCASE = [
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

    assert references == FEATURED_EXPLAINERS
    assert "api.star-history.com/chart" in text
    assert "Ask a question. Get a visual explainer." in text
    assert "docs/showcase/README.md" in text


def test_every_featured_explainer_asset_exists():
    for asset in FEATURED_EXPLAINERS:
        assert Path(asset).is_file()


def test_old_mythos_showcase_is_absent_from_root_readme():
    text = readme_text()

    for asset in REMOVED_MYTHOS_SHOWCASE:
        assert asset not in text

    for title in [
        "THE TRAITOR AXIS",
        "VORTEX LEAPFROG",
        "THE VALLEY OF STABILITY",
        "EXCEPTIONAL POINT MONODROMY",
    ]:
        assert title not in text


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


def test_mcp_onboarding_includes_setup_and_conversation():
    text = readme_text()

    assert "## Make Your First Explainer" in text
    assert 'pip install -e ".[mcp]"' in text
    assert '"args": ["serve-mcp"]' in text
    assert "Use Math To Manim to create a visual explainer" in text
    assert "The assistant starts the explainer" in text
    assert "The assistant reports progress" in text
    assert "The assistant can inspect every reasoning artifact" in text


def test_native_pipelines_and_related_kimi_repo_are_clear():
    text = readme_text()

    assert "## Choose A Native Pipeline" in text
    assert "math-to-manim run" in text
    assert "math-to-manim-sol run" in text
    assert "Neither pipeline routes through the other" in text
    assert "https://github.com/HarleyCoops/KimiK3Manim" in text
    assert "different enough to warrant its own repository" in text


def prose_without_code_or_links(text: str) -> str:
    alt_text = " ".join(re.findall(r'alt="([^"]*)"', text))
    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    prose = re.sub(r"`[^`]*`", "", prose)
    prose = re.sub(r"<[^>]+>", "", prose)
    prose = re.sub(r"\]\([^)]+\)", "]", prose)
    return f"{prose}\n{alt_text}"


def test_legacy_root_material_is_removed():
    text = readme_text()
    forbidden = [
        "docs/showcase/assets/the-last-day.gif",
        "docs/showcase/assets/associate-family-riso.gif",
        "docs/showcase/assets/blueprint-holonomy.gif",
        "docs/showcase/assets/reverse-reasoning-tree.gif",
        "docs/showcase/assets/mythos-grammar-reel.gif",
        "## What's new in v1.1",
        "## The morning it started",
        "## Motion showcase",
    ]
    for item in forbidden:
        assert item not in text


def test_technical_reference_remains_complete():
    text = readme_text()
    required = [
        "## Installation",
        "## Run Artifacts",
        "## MCP Reference",
        "## REST API",
        "## Configuration",
        "## Testing",
        "## Repository Layout",
        "## License",
    ]
    for heading in required:
        assert heading in text


def test_written_prose_contains_no_dash_punctuation():
    prose = prose_without_code_or_links(readme_text())

    assert "—" not in prose
    assert "–" not in prose
    assert re.search(r"(?<=[A-Za-z])-(?=[A-Za-z])", prose) is None
