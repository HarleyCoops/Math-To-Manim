"""Operator entry for ``math-to-manim-mythos serve-mcp``.

The MCP tools are Grok-native and live in ``grok.mcp_server``. This module
re-exports the server object and its ``main`` so the Mythos CLI command and
``python -m mythos.cli serve-mcp`` keep serving the same tool names.
"""

from grok.mcp_server import main, mcp  # noqa: F401

__all__ = ["main", "mcp"]
