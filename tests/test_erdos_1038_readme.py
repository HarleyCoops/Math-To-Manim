from pathlib import Path


def test_user_requested_erdos_homepage_removal():
    text=Path('README.md').read_text(encoding='utf-8')
    assert 'erdos-1038-potential-landscape.gif' not in text
    assert 'landscape made by its roots' not in text
    assert 'api.star-history.com/chart' in text


def test_erdos_archive_media_preserved():
    for extension in ('gif','mp4'):
        assert Path(f'docs/showcase/assets/erdos-1038-potential-landscape.{extension}').is_file()
    assert Path('docs/prompts/erdos-1038-off-white-3d.md').is_file()
