import re
from pathlib import Path


README = Path("README.md")


def test_erdos_1038_is_the_first_readme_animation():
    text = README.read_text(encoding="utf-8")
    first_gif = re.search(r"docs/showcase/assets/[^\"']+\.gif", text)

    assert first_gif is not None
    assert first_gif.group() == (
        "docs/showcase/assets/erdos-1038-potential-landscape.gif"
    )
    assert "api.star-history.com/chart" in text
    assert "docs/showcase/assets/jacobian-conjecture-3d.gif" in text
    assert "docs/showcase/assets/traitor-axis.gif" not in text


def test_erdos_1038_readme_media_and_explanation_are_complete():
    text = README.read_text(encoding="utf-8")

    assert Path(
        "docs/showcase/assets/erdos-1038-potential-landscape.gif"
    ).is_file()
    assert Path(
        "docs/showcase/assets/erdos-1038-potential-landscape.mp4"
    ).is_file()
    assert "landscape made by its roots" in text
    assert "1.834430475762661" in text
    assert "2√2" in text
    assert "Watch the complete 79 second visual explainer" in text
