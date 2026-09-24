"""Build the same lesson for a static host; no run logs or credentials exported."""
from pathlib import Path
import shutil
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "lesson"


def build():
    (OUT / "web").mkdir(parents=True, exist_ok=True)
    (OUT / "films").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "web/index.html", OUT / "index.html")
    for name in ("lesson.js", "style.css"):
        shutil.copyfile(ROOT / "web" / name, OUT / "web" / name)
    for name in ("the-third-side.mp4", "the-third-side.gif", "the-third-side-poster.png"):
        shutil.copyfile(ROOT / "docs/showcase/assets" / name, OUT / "films" / name)
    (OUT / "health.json").write_text(json.dumps({"status": "ok", "lesson": "the-third-side"}))
    (OUT / ".nojekyll").touch()
    print(OUT)


if __name__ == "__main__":
    build()
