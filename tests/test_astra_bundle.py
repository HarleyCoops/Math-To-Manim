"""Release bundling cannot mislabel stale or modified film evidence as completed."""
import hashlib
import json
import pytest
from scripts.build_astra_bundle import validate_film


@pytest.fixture
def film(tmp_path):
    paper = tmp_path / 'paper'
    media = tmp_path / 'film'
    paper.mkdir(); media.mkdir()
    candidate = paper / 'candidate.json'
    candidate.write_text(json.dumps({'content': 'retained scene'}))
    movie = media / 'quasi-riemann-720p.mp4'
    movie.write_bytes(b'retained film')
    manifest = {'status': 'completed', 'source_candidate_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
                'video_sha256': hashlib.sha256(movie.read_bytes()).hexdigest(), 'review_status': 'not_reviewed'}
    evidence = {'video_sha256': manifest['video_sha256'],
                'rendered_source_sha256': hashlib.sha256(b'retained scene').hexdigest()}
    (media / 'quasi-riemann-render-manifest.json').write_text(json.dumps(manifest))
    (media / 'quasi-riemann-film-evidence.json').write_text(json.dumps(evidence))
    return paper, media


def test_completed_film_retains_review_scope(film):
    assert validate_film(*film)['review_status'] == 'not_reviewed'


def test_modified_movie_is_rejected(film):
    paper, media = film
    (media / 'quasi-riemann-720p.mp4').write_bytes(b'modified film')
    with pytest.raises(ValueError, match='Film bytes'):
        validate_film(paper, media)


def test_stale_scene_is_rejected(film):
    paper, media = film
    (paper / 'candidate.json').write_text(json.dumps({'content': 'a different scene'}))
    with pytest.raises(ValueError, match='retained candidate'):
        validate_film(paper, media)
