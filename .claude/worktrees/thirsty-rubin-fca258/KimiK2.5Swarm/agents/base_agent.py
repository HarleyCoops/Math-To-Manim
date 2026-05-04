"""
Base Agent - Role-based agent foundation for enrichment pipeline.

Provides:
- AgentRole enum for different agent types
- Role-specific system prompts
- AgentResult dataclass for structured outputs
- BaseAgent class with tool calling loop

Example:
    from agents.base_agent import BaseAgent, AgentRole

    agent = BaseAgent(
        role=AgentRole.MATHEMATICAL,
        task="Enrich node with equations",
        tools=math_tools,
        tool_map=tool_map,
    )

    result = await agent.execute()
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from kimi_client import KimiClient, KimiResponse

logger = logging.getLogger(__name__)


# =============================================================================
# Agent Roles
# =============================================================================


class AgentRole(Enum):
    """
    Roles for enrichment agents.

    Each role has a specific system prompt and purpose.
    """
    MATHEMATICAL = "mathematical"
    VISUAL = "visual"
    NARRATIVE = "narrative"
    PREREQUISITE = "prerequisite"
    VERIFIER = "verifier"
    RESEARCHER = "researcher"


# Role-specific system prompts
ROLE_PROMPTS: Dict[AgentRole, str] = {
    AgentRole.MATHEMATICAL: """You are a Mathematical Enrichment Agent.

Your role is to add rigorous mathematical content to concepts:
- Provide 2-5 LaTeX equations formatted for MathTex
- Define every symbol used in the equations
- Explain the physical or mathematical meaning
- Include worked examples where appropriate
- Note typical values or constants

Always respond by calling the appropriate tool with structured data.
Do not include plain text responses outside of tool calls.""",

    AgentRole.VISUAL: """You are a Visual Design Agent.

Your role is to design visual presentations for Manim animations:
- Describe what should appear visually (objects, shapes, elements)
- Specify color schemes using descriptive names
- Describe animations as visual effects (rotate, fade, zoom)
- Plan transitions between concepts
- Estimate scene duration (10-40 seconds)

Focus on what should be shown, not Manim implementation details.
Always respond by calling the appropriate tool.""",

    AgentRole.NARRATIVE: """You are a Narrative Composition Agent.

Your role is to compose comprehensive narratives for animations:
- Walk through concepts from foundations to target
- Reference LaTeX equations exactly as provided
- Describe visual elements naturally
- Integrate timing and pacing suggestions
- Create a cohesive educational story

Aim for 2000+ words that guide Manim code generation.
Always respond by calling the appropriate tool.""",

    AgentRole.PREREQUISITE: """You are a Prerequisite Discovery Agent.

Your role is to identify essential prerequisite concepts:
- Find concepts necessary for understanding (not just helpful)
- Order from most to least important
- Assume high school education as baseline
- Be specific (prefer "special relativity" over "relativity")
- Limit to 3-5 prerequisites maximum

Always respond with structured JSON data.""",

    AgentRole.VERIFIER: """You are a Verification Agent.

Your role is to verify enrichment quality:
- Check equations for correctness
- Verify definitions are accurate
- Ensure visual designs are feasible
- Validate narrative coherence
- Flag any issues or inconsistencies

Provide structured feedback for improvements.""",

    AgentRole.RESEARCHER: """You are a Research Agent.

Your role is to gather information and context:
- Search for relevant facts and evidence
- Cite sources accurately
- Provide comprehensive background
- Identify key relationships between concepts

Always provide well-organized, factual information.""",
}


# =============================================================================
# Agent Configuration and Results
# =============================================================================


@dataclass
class AgentConfig:
    """
    Configuration for agent execution.

    Attributes:
        max_steps: Maximum tool calling iterations
        temperature: Sampling temperature
        max_tokens: Maximum tokens per response
        timeout: Total execution timeout in seconds
    """
    max_steps: int = 100
    temperature: float = 1.0
    max_tokens: int = 4096
    timeout: int = 300


@dataclass
class AgentResult:
    """
    Result from agent execution.

    Attributes:
        agent_id: Unique identifier for this execution
        role: The agent's role
        task: The task that was executed
        output: The final output (tool result or text)
        success: Whether execution completed successfully
        error: Error message if execution failed
        tool_calls_made: Number of tool calls during execution
        execution_time_seconds: Total execution time
        reasoning: Collected reasoning traces (if in thinking mode)
    """
    agent_id: str
    role: AgentRole
    task: str
    output: Any = None
    success: bool = True
    error: Optional[str] = None
    tool_calls_made: int = 0
    execution_time_seconds: float = 0.0
    reasoning: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "task": self.task,
            "output": self.output,
            "success": self.success,
            "error": self.error,
            "tool_calls_made": self.tool_calls_made,
            "execution_time_seconds": self.execution_time_seconds,
            "reasoning": self.reasoning,
        }


# =============================================================================
# Base Agent Class
# =============================================================================


class BaseAgent:
    """
    Base class for enrichment agents.

    Provides core functionality for:
    - Role-based system prompts
    - Tool calling loop
    - Async execution
    - Result tracking
    """

    def __init__(
        self,
        role: AgentRole,
        task: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_map: Optional[Dict[str, Callable]] = None,
        client: Optional['KimiClient'] = None,
        config: Optional[AgentConfig] = None,
    ):
        """
        Initialize the agent.

        Args:
            role: The agent's role
            task: The task description
            tools: Tool definitions in OpenAI format
            tool_map: Mapping of tool names to functions
            client: KimiClient instance (created if not provided)
            config: Agent configuration
        """
        self.role = role
        self.task = task
        self.tools = tools or []
        self.tool_map = tool_map or {}
        self.config = config or AgentConfig()
        self.agent_id = str(uuid.uuid4())[:8]

        # Get system prompt for role
        self.system_prompt = ROLE_PROMPTS.get(role, "")

        # Initialize client lazily
        self._client = client
        self._steps = 0
        self._tool_calls_made = 0

    @property
    def client(self) -> 'KimiClient':
        """Get or create the Kimi client."""
        if self._client is None:
            from kimi_client import get_kimi_client
            self._client = get_kimi_client()
        return self._client

    async def execute(self) -> AgentResult:
        """
        Execute the agent's task.

        Returns:
            AgentResult with execution details
        """
        start_time = time.time()
        reasoning_trace = []

        try:
            # Use tool calling loop
            from kimi_client import KimiMode

            response = self.client.execute_with_tools(
                message=self.task,
                tools=self.tools,
                tool_map=self.tool_map,
                mode=KimiMode.AGENT,
                system_prompt=self.system_prompt,
                max_steps=self.config.max_steps,
                on_tool_call=lambda name, args: self._on_tool_call(name, args),
            )

            execution_time = time.time() - start_time

            # Collect reasoning if available
            reasoning = response.reasoning
            if reasoning_trace:
                reasoning = "\n".join(reasoning_trace)

            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                task=self.task,
                output=response.content,
                success=True,
                tool_calls_made=self._tool_calls_made,
                execution_time_seconds=execution_time,
                reasoning=reasoning,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Agent {self.agent_id} failed: {e}")

            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                task=self.task,
                output=None,
                success=False,
                error=str(e),
                tool_calls_made=self._tool_calls_made,
                execution_time_seconds=execution_time,
            )

    def _on_tool_call(self, name: str, args: Dict[str, Any]) -> None:
        """Callback for tool calls."""
        self._tool_calls_made += 1
        logger.debug(f"Agent {self.agent_id} calling tool: {name}")

    async def execute_simple(self) -> AgentResult:
        """
        Execute without tool loop (single call).

        Useful for simple tasks that don't require multiple iterations.
        """
        start_time = time.time()

        try:
            from kimi_client import KimiMode

            response = self.client.chat(
                message=self.task,
                mode=KimiMode.THINKING,
                system_prompt=self.system_prompt,
                tools=self.tools if self.tools else None,
            )

            execution_time = time.time() - start_time

            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                task=self.task,
                output=response.content,
                success=True,
                execution_time_seconds=execution_time,
                reasoning=response.reasoning,
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                task=self.task,
                output=None,
                success=False,
                error=str(e),
                execution_time_seconds=execution_time,
            )

    def execute_sync(self) -> AgentResult:
        """Synchronous wrapper for execute()."""
        return asyncio.run(self.execute())


# =============================================================================
# Specialized Agent Factories
# =============================================================================


def create_mathematical_agent(
    task: str,
    client: Optional['KimiClient'] = None,
) -> BaseAgent:
    """Create a mathematical enrichment agent."""
    from tools import MATH_TOOLS, get_default_registry

    registry = get_default_registry()

    return BaseAgent(
        role=AgentRole.MATHEMATICAL,
        task=task,
        tools=registry.get_openai_tools(category="math"),
        tool_map=registry.get_tool_map(category="math"),
        client=client,
    )


def create_visual_agent(
    task: str,
    client: Optional['KimiClient'] = None,
) -> BaseAgent:
    """Create a visual design agent."""
    from tools import get_default_registry

    registry = get_default_registry()

    return BaseAgent(
        role=AgentRole.VISUAL,
        task=task,
        tools=registry.get_openai_tools(category="visual"),
        tool_map=registry.get_tool_map(category="visual"),
        client=client,
    )


def create_narrative_agent(
    task: str,
    client: Optional['KimiClient'] = None,
) -> BaseAgent:
    """Create a narrative composition agent."""
    from tools import get_default_registry

    registry = get_default_registry()

    return BaseAgent(
        role=AgentRole.NARRATIVE,
        task=task,
        tools=registry.get_openai_tools(category="narrative"),
        tool_map=registry.get_tool_map(category="narrative"),
        client=client,
    )
