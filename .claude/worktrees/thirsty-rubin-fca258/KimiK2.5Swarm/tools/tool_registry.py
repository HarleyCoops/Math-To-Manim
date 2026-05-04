"""
Kimi K2.5 Tool Registry - Centralized tool management.

Provides:
- Tool registration and discovery
- Schema validation
- Dynamic tool loading
- Tool categorization and tagging
- Dual export (OpenAI format + tool map)

Example:
    from tools import ToolRegistry

    registry = ToolRegistry()

    # Register a tool
    registry.register(
        name="calculate",
        func=calculate_func,
        description="Perform calculations",
        parameters={
            "type": "object",
            "required": ["expression"],
            "properties": {
                "expression": {"type": "string"}
            }
        }
    )

    # Get tools for API
    tools = registry.get_openai_tools()
    tool_map = registry.get_tool_map()
"""

from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, get_type_hints

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """
    Representation of a registered tool.

    Attributes:
        name: Unique tool name
        func: The callable function
        description: Human-readable description
        parameters: JSON schema for parameters
        category: Tool category for filtering
        tags: Additional tags for discovery
        enabled: Whether the tool is currently enabled
        requires_auth: Whether the tool requires authentication
    """
    name: str
    func: Callable
    description: str
    parameters: Dict[str, Any]
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    requires_auth: bool = False

    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def __call__(self, *args, **kwargs):
        """Make the tool callable."""
        return self.func(*args, **kwargs)


class ToolRegistry:
    """
    Registry for managing tools available to Kimi K2.5.

    Features:
    - Register tools with schemas
    - Get tools by category/tags
    - Enable/disable tools dynamically
    - Export to OpenAI format
    """

    def __init__(self):
        """Initialize empty registry."""
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[str, List[str]] = {}

    def register(
        self,
        name: str,
        func: Callable,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        category: str = "general",
        tags: Optional[List[str]] = None,
        requires_auth: bool = False,
    ) -> Tool:
        """
        Register a new tool.

        Args:
            name: Unique tool name
            func: The callable function
            description: Human-readable description (auto-generated from docstring if None)
            parameters: JSON schema for parameters (auto-inferred if None)
            category: Tool category for filtering
            tags: Additional tags for discovery
            requires_auth: Whether the tool requires authentication

        Returns:
            The registered Tool instance

        Raises:
            ValueError: If a tool with the same name already exists
        """
        if name in self._tools:
            raise ValueError(f"Tool '{name}' already registered")

        # Auto-generate description from docstring if not provided
        if description is None:
            description = func.__doc__ or f"Execute {name}"
            description = description.strip().split('\n')[0]

        # Auto-infer parameters from function signature if not provided
        if parameters is None:
            parameters = self._infer_parameters(func)

        tool = Tool(
            name=name,
            func=func,
            description=description,
            parameters=parameters,
            category=category,
            tags=tags or [],
            requires_auth=requires_auth,
        )

        self._tools[name] = tool

        # Update category index
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)

        logger.debug(f"Registered tool: {name} (category: {category})")
        return tool

    def _infer_parameters(self, func: Callable) -> Dict[str, Any]:
        """
        Infer JSON schema parameters from function signature.

        Args:
            func: The function to analyze

        Returns:
            JSON schema dictionary
        """
        sig = inspect.signature(func)
        properties: Dict[str, Any] = {}
        required: List[str] = []

        # Try to get type hints
        try:
            hints = get_type_hints(func)
        except Exception:
            hints = {}

        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue

            # Determine type from hint or default
            param_type = "string"  # default
            if param_name in hints:
                hint = hints[param_name]
                if hint == int:
                    param_type = "integer"
                elif hint == float:
                    param_type = "number"
                elif hint == bool:
                    param_type = "boolean"
                elif hint == list or (hasattr(hint, '__origin__') and hint.__origin__ == list):
                    param_type = "array"
                elif hint == dict or (hasattr(hint, '__origin__') and hint.__origin__ == dict):
                    param_type = "object"

            properties[param_name] = {"type": param_type}

            # Add description from parameter annotation if available
            if param.annotation != inspect.Parameter.empty and isinstance(param.annotation, str):
                properties[param_name]["description"] = param.annotation

            # Determine if required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_openai_tools(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        enabled_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Export tools in OpenAI function calling format.

        Args:
            category: Filter by category (None = all)
            tags: Filter by tags (None = all)
            enabled_only: Only include enabled tools

        Returns:
            List of tool schemas in OpenAI format
        """
        tools = []
        for tool in self._tools.values():
            # Filter by enabled status
            if enabled_only and not tool.enabled:
                continue

            # Filter by category
            if category and tool.category != category:
                continue

            # Filter by tags
            if tags and not any(tag in tool.tags for tag in tags):
                continue

            tools.append(tool.to_openai_schema())

        return tools

    def get_tool_map(
        self,
        category: Optional[str] = None,
        enabled_only: bool = True,
    ) -> Dict[str, Callable]:
        """
        Get mapping of tool names to callable functions.

        Args:
            category: Filter by category (None = all)
            enabled_only: Only include enabled tools

        Returns:
            Dictionary mapping tool names to functions
        """
        tool_map = {}
        for name, tool in self._tools.items():
            if enabled_only and not tool.enabled:
                continue
            if category and tool.category != category:
                continue
            tool_map[name] = tool.func

        return tool_map

    def enable(self, name: str) -> None:
        """Enable a tool."""
        if name in self._tools:
            self._tools[name].enabled = True
            logger.debug(f"Enabled tool: {name}")

    def disable(self, name: str) -> None:
        """Disable a tool."""
        if name in self._tools:
            self._tools[name].enabled = False
            logger.debug(f"Disabled tool: {name}")

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """List all registered tool names."""
        if category:
            return self._categories.get(category, [])
        return list(self._tools.keys())

    def list_categories(self) -> List[str]:
        """List all registered categories."""
        return list(self._categories.keys())

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._categories.clear()

    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools


# =============================================================================
# Default Registry Singleton
# =============================================================================


_default_registry: Optional[ToolRegistry] = None


def get_default_registry() -> ToolRegistry:
    """
    Get or create the default tool registry.

    Returns:
        The default ToolRegistry instance
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = ToolRegistry()
        _register_builtin_tools(_default_registry)
    return _default_registry


def _register_builtin_tools(registry: ToolRegistry) -> None:
    """Register built-in tools to the registry."""
    from .builtin_tools import register_enrichment_tools
    register_enrichment_tools(registry)
