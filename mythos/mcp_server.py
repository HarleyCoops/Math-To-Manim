"""Operator entry for ``math-to-manim serve-mcp``.

The MCP tools are Grok-native. This module re-exports ``grok.mcp_server``
so existing clients keep the same command and tool names.
"""

from grok.mcp_server import (  # noqa: F401
    ArtifactInput,
    CreateAnimationInput,
    ListRunsInput,
    RunIdInput,
    main,
    mcp,
    m2m_cinematic_charter,
    m2m_create_animation,
    m2m_get_artifact,
    m2m_get_job,
    m2m_get_run,
    m2m_get_scene_code,
    m2m_list_runs,
)

# Tests and callers patch `_service` on this module; keep it bound here
# and on grok.mcp_server so both names see the same object unless patched.
from grok.mcp_server import _service  # noqa: F401, E402
