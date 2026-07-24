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
