"""Preserve the existing gallery while allowing the story and copy to evolve."""
import re
from pathlib import Path

PRESERVED_GIFS = ['docs/showcase/assets/circle-area-3d-unwrapped.gif', 'docs/showcase/assets/cosmic-gravity-3d.gif', 'docs/showcase/assets/erdos-1038-potential-landscape.gif', 'docs/showcase/assets/exceptional-point-monodromy.gif', 'docs/showcase/assets/fourier-epicycles.gif', 'docs/showcase/assets/grpo-semantic-manifold.gif', 'docs/showcase/assets/hopf-fibration.gif', 'docs/showcase/assets/jacobian-conjecture-3d.gif', 'docs/showcase/assets/lorenz-attractor.gif', 'docs/showcase/assets/mythos-grammar-reel.gif', 'docs/showcase/assets/olin-off-white-3d-space.gif', 'docs/showcase/assets/qed-minkowski-epic-3d.gif', 'docs/showcase/assets/reverse-reasoning-tree.gif']

def test_requested_homepage_cleanup_preserves_archived_assets():
    text=Path('README.md').read_text(encoding='utf-8')
    assert 'Featured Visual Explainers' not in text
    assert 'ERDŐS 1038: THE POTENTIAL LANDSCAPE' not in text
    assert 'OLIN: THE SPACE INSIDE A TWEET' not in text
    assert 'TypeSafe' in text and 'jev-1.13.0' in text
    assert '```mermaid' in text
    for asset in PRESERVED_GIFS:
        assert Path(asset).is_file()
    assert 'api.star-history.com/chart' in text

def test_local_readme_media_resolve():
    text=Path("README.md").read_text(encoding="utf-8")
    for path in re.findall(r'(?:src|href)="(docs/[^"?#]+)"', text):
        assert Path(path).is_file(), path

def test_creation_evidence_and_experiment_remain_accessible():
    text=Path("README.md").read_text(encoding="utf-8")
    assert "09a2f22ec02b0374d38373d28f76c5764a1e9a2e" in text
    assert "5a56bdbde75a16bdfbf3a8e9c852be3dfcfb8eef" in text
    assert "docs/JEV.md" in text
    assert "environments/m2m2_visual_improvement/README.md" in text

def test_technical_reference_remains_accessible():
    text=Path("README.md").read_text(encoding="utf-8")
    for heading in ["Installation","Run Artifacts","Testing","License"]:
        assert f"## {heading}" in text
