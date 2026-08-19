import re
from pathlib import Path


README = Path("README.md")
SHOWCASE = Path("docs/showcase/README.md")

FEATURED_EXPLAINERS = [
    "docs/showcase/assets/erdos-1038-potential-landscape.gif",
    "docs/showcase/assets/olin-off-white-3d-space.gif",
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


def test_olin_feature_links_the_film_prompt_and_scene():
    text = readme_text()

    required = [
        'href="docs/showcase/assets/olin-off-white-3d-space.mp4"',
        'src="docs/showcase/assets/olin-off-white-3d-space.gif"',
        'href="docs/prompts/olin-off-white-3d-space.md"',
        'href="examples/mythos/olin_off_white_3d_space.py"',
        "The first construction is the exact lift",
        "This is an alternate cylindrical interpretation",
        "Its projection does not reproduce the original drawing",
    ]
    for item in required:
        assert item in text


def test_olin_showcase_links_the_film_and_lists_the_asset():
    text = SHOWCASE.read_text(encoding="utf-8")

    required = [
        'href="assets/olin-off-white-3d-space.mp4"',
        'src="assets/olin-off-white-3d-space.gif"',
        "[corrected Mythos prompt](../prompts/olin-off-white-3d-space.md)",
        "[Manim scene](../../examples/mythos/olin_off_white_3d_space.py)",
        "| `assets/olin-off-white-3d-space.gif` | Generative art / geometry |",
        "exact lift",
        "alternate interpretation",
    ]
    for item in required:
        assert item in text


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


def test_grok_onboarding_includes_key_doctor_and_first_run():
    text = readme_text()

    assert "## Make Your First Explainer" in text
    assert 'pip install -e ".[dev,grok,render]"' in text
    assert "XAI_API_KEY" in text
    assert "math-to-manim-grok doctor" in text
    assert "math-to-manim-grok run" in text
    assert "--offline" in text
    assert "--image" in text
    assert "It never prints the key" in text


def test_readme_features_grok_only():
    text = readme_text()

    assert "## Choose A Native Pipeline" not in text
    assert "math-to-manim-sol" not in text
    assert "Neither pipeline routes through the other" not in text
    assert "Claude CLI" not in text
    assert "Codex" not in text
    assert "Grok 4.6" in text
    assert "math-to-manim-grok run" in text
    assert "reverse thinking" in text


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


def test_front_page_stays_a_story():
    text = readme_text()

    assert "## Make A Custom Bot" in text
    assert "## License" in text
    assert "docs/GROK_4_6_SILO.md" in text
    for heading in [
        "## Installation",
        "## Run Artifacts",
        "## Configuration",
        "## Testing",
        "## Repository Layout",
        "## MCP Reference",
        "## REST API",
    ]:
        assert heading not in text
    assert "| Variable | Default | Purpose |" not in text
    assert "| Method | Route | Purpose |" not in text
    assert "| Tool | Purpose |" not in text


def test_written_prose_contains_no_dash_punctuation():
    prose = prose_without_code_or_links(readme_text())

    assert "—" not in prose
    assert "–" not in prose
    assert re.search(r"(?<=[A-Za-z])-(?=[A-Za-z])", prose) is None
