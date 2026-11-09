"""Each provider silo in src/ is an independent implementation.

See docs/*_SILO.md. A silo may not import another silo. There are no
exceptions: each silo that serves MCP has its own ``mcp_server`` module.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
SILOS = sorted(p.name for p in SRC.iterdir() if (p / "__init__.py").is_file())
ALLOWED: set[tuple[str, str]] = set()


def _imported_tops(tree: ast.AST) -> set[str]:
    tops: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            tops.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            tops.add(node.module.split(".")[0])
    return tops


def test_every_silo_is_found():
    assert set(SILOS) >= {"argon", "astra", "glm", "grok", "mimo", "mythos", "sol"}


def test_no_silo_imports_another_silo():
    violations = []
    for silo in SILOS:
        for path in (SRC / silo).rglob("*.py"):
            rel = path.relative_to(SRC).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for top in _imported_tops(tree) & set(SILOS) - {silo}:
                if (rel, top) not in ALLOWED:
                    violations.append(f"{rel} imports {top}")
    assert violations == []
