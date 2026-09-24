from fastapi.testclient import TestClient
from deployment.app import app


def test_public_lesson_serves_page_assets_and_health_without_agent_routes():
    with TestClient(app) as client:
        assert client.get('/health').json() == {'status': 'ok', 'lesson': 'the-third-side'}
        page = client.get('/')
        assert page.status_code == 200
        assert 'The third' in page.text
        assert client.get('/web/lesson.js').status_code == 200
        assert client.get('/web/style.css').status_code == 200
        assert client.post('/v1/runs', json={'prompt': 'test'}).status_code == 404
        assert client.get('/runs/sol/manifest.json').status_code == 404


def test_published_video_supports_range_requests():
    with TestClient(app) as client:
        response = client.get('/films/the-third-side.mp4', headers={'Range': 'bytes=0-99'})
        assert response.status_code == 206
        assert len(response.content) == 100
        assert response.headers['content-type'] == 'video/mp4'
