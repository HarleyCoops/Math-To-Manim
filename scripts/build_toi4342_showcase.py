"""Wrap the editable 3D scene as a standalone browser lesson, without model calls."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "docs/showcase/toi4342-third-signal"
SOURCE = SHOWCASE / "interactive-scene.html"
OUTPUT = SHOWCASE / "interactive.html"


def main():
    fragment = SOURCE.read_text(encoding="utf-8")
    shell = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The third rhythm · TOI-4342</title>
<style>
:root {
  color-scheme:light dark;
  --background:light-dark(#ffffff,#171717); --foreground:light-dark(#202020,#f1f1f1);
  --muted-foreground:light-dark(#555555,#bdbdbd); --border:light-dark(#d0d0d0,#555555);
  --primary:light-dark(#222222,#e7e7e7); --primary-foreground:light-dark(#ffffff,#1a1a1a);
  --orange:light-dark(#bc6a2c,#ef9759);
  --viz-series-1:light-dark(#356b9e,#8ab9e6);
  --viz-series-2:light-dark(#a35f25,#e5a06a);
  --viz-series-3:light-dark(#39835a,#86b68c);
}
*{box-sizing:border-box}body{margin:0;background:var(--background);color:var(--foreground);font:16px system-ui}
main{max-width:1100px;margin:auto;padding:24px}h3{font-size:1.25rem;font-weight:500;margin:0 0 18px}
.viz-controls{display:flex;align-items:flex-end;flex-wrap:wrap;gap:8px}
.form-label{display:flex;flex-direction:column;gap:6px;flex:1;min-width:230px}
.form-select,.btn{font:inherit;color:var(--foreground);background:var(--background);border:1px solid var(--border);border-radius:7px;padding:9px 12px}
.btn{cursor:pointer}.btn[aria-pressed=true]{background:var(--primary);color:var(--primary-foreground)}
.text-small{font-size:.875rem}button:focus-visible,select:focus-visible{outline:2px solid var(--viz-series-1);outline-offset:3px}
footer{font-size:.875rem;color:var(--muted-foreground);margin-top:22px}a{color:inherit}
@media(max-width:500px){main{padding:16px}.form-label{flex-basis:100%}}
</style></head><body><main>
"""
    footer = """
<footer>Based on <a href="https://github.com/eumemic/exoplanets/tree/ec8311b19a61092ad5eae3d34e947b14485d363e">eumemic/exoplanets</a> and <a href="https://arxiv.org/html/2301.01370v1">Tey et al. (2023)</a>.
Drag to rotate; scroll to zoom. Orbit shapes, phases and surfaces are illustrative.
The 18.908-day signal is a candidate. <a href="README.md">Sources and production record</a>.</footer>
</main></body></html>
"""
    OUTPUT.write_text(shell + fragment + footer, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
