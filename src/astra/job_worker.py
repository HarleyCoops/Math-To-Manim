"""Operator worker for the existing Astra/Jev pipeline, owned by its MCP server."""
import json
from pathlib import Path
import sys

from astra.pipeline import Pipeline, save


def main(folder):
    folder = Path(folder).resolve()
    try:
        Pipeline().run(None, folder=folder)
    except Exception as exc:
        manifest = folder / 'manifest.json'
        state = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {}
        state.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        save(manifest, state)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
