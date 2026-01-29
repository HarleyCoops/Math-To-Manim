"""
Parallel Tool Executor - Concurrent execution with semaphore control.

Provides high-performance parallel execution of tool calls with:
- Semaphore-controlled concurrency (up to 100+ concurrent)
- Automatic retry with exponential backoff
- Timeout management
- Execution metrics tracking
- Both sync and async function support
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """
    Result of a single tool execution.

    Attributes:
        tool_call_id: Unique identifier for this tool call
        tool_name: Name of the executed tool
        result: The return value from the tool
        success: Whether execution succeeded
        error: Error message if execution failed
        execution_time_ms: Execution time in milliseconds
    """
    tool_call_id: str
    tool_name: str
    result: Any
    success: bool = True
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_message(self) -> Dict[str, Any]:
        """Convert to tool result message format for API."""
        content = self.result if self.success else f"Error: {self.error}"
        if not isinstance(content, str):
            import json
            content = json.dumps(content)

        return {
            "role": "tool",
            "tool_call_id": self.tool_call_id,
            "content": content,
        }


@dataclass
class BatchResult:
    """
    Result of a batch tool execution.

    Attributes:
        results: Individual tool results
        total_time_ms: Total batch execution time
        successful_count: Number of successful executions
        failed_count: Number of failed executions
    """
    results: List[ToolResult] = field(default_factory=list)
    total_time_ms: float = 0.0
    successful_count: int = 0
    failed_count: int = 0

    @property
    def all_successful(self) -> bool:
        """Check if all executions succeeded."""
        return self.failed_count == 0

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all results as API messages."""
        return [r.to_message() for r in self.results]


class ParallelToolExecutor:
    """
    Execute tool calls concurrently with controlled parallelism.

    Features:
    - Semaphore-based concurrency control
    - Automatic retry with exponential backoff
    - Timeout management per call
    - Metrics tracking
    - Support for both sync and async tools

    Example:
        executor = ParallelToolExecutor(max_concurrent=50)

        tool_calls = [
            {"id": "1", "function": {"name": "search", "arguments": '{"q": "test"}'}},
            {"id": "2", "function": {"name": "calculate", "arguments": '{"expr": "1+1"}'}},
        ]

        result = await executor.execute_batch(tool_calls, tool_map)
        print(f"Completed {result.successful_count} calls")
    """

    def __init__(
        self,
        max_concurrent: int = 100,
        timeout_per_call: float = 60.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the parallel executor.

        Args:
            max_concurrent: Maximum concurrent executions
            timeout_per_call: Timeout per tool call in seconds
            retry_attempts: Number of retry attempts on failure
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.max_concurrent = max_concurrent
        self.timeout_per_call = timeout_per_call
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self._semaphore: Optional[asyncio.Semaphore] = None

    def _get_semaphore(self) -> asyncio.Semaphore:
        """Get or create the semaphore for the current event loop."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore

    async def execute_batch(
        self,
        tool_calls: List[Dict[str, Any]],
        tool_map: Dict[str, Callable],
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> BatchResult:
        """
        Execute multiple tool calls in parallel.

        Args:
            tool_calls: List of tool call dictionaries with id, function.name, function.arguments
            tool_map: Dictionary mapping tool names to callable functions
            on_progress: Optional callback(completed, total) for progress tracking

        Returns:
            BatchResult with all execution results
        """
        start_time = time.time()
        total = len(tool_calls)
        completed = 0

        async def execute_with_progress(call: Dict[str, Any]) -> ToolResult:
            nonlocal completed
            result = await self._execute_single(call, tool_map)
            completed += 1
            if on_progress:
                on_progress(completed, total)
            return result

        # Create tasks for all tool calls
        tasks = [execute_with_progress(call) for call in tool_calls]

        # Execute all tasks concurrently (semaphore controls actual parallelism)
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        batch_result = BatchResult()
        for result in results:
            if isinstance(result, Exception):
                # Handle unexpected exceptions
                batch_result.results.append(ToolResult(
                    tool_call_id="unknown",
                    tool_name="unknown",
                    result=None,
                    success=False,
                    error=str(result),
                ))
                batch_result.failed_count += 1
            else:
                batch_result.results.append(result)
                if result.success:
                    batch_result.successful_count += 1
                else:
                    batch_result.failed_count += 1

        batch_result.total_time_ms = (time.time() - start_time) * 1000
        return batch_result

    async def _execute_single(
        self,
        tool_call: Dict[str, Any],
        tool_map: Dict[str, Callable],
    ) -> ToolResult:
        """Execute a single tool call with retry logic."""
        import json

        semaphore = self._get_semaphore()

        # Extract tool call details
        call_id = tool_call.get("id", "unknown")
        function = tool_call.get("function", {})
        tool_name = function.get("name", "unknown")
        arguments_str = function.get("arguments", "{}")

        # Parse arguments
        try:
            arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
        except json.JSONDecodeError as e:
            return ToolResult(
                tool_call_id=call_id,
                tool_name=tool_name,
                result=None,
                success=False,
                error=f"Invalid JSON arguments: {e}",
            )

        # Get the tool function
        if tool_name not in tool_map:
            return ToolResult(
                tool_call_id=call_id,
                tool_name=tool_name,
                result=None,
                success=False,
                error=f"Unknown tool: {tool_name}",
            )

        tool_func = tool_map[tool_name]

        # Execute with retry
        last_error = None
        for attempt in range(self.retry_attempts):
            try:
                async with semaphore:
                    start_time = time.time()

                    # Execute the tool (handle both sync and async)
                    if asyncio.iscoroutinefunction(tool_func):
                        result = await asyncio.wait_for(
                            tool_func(**arguments),
                            timeout=self.timeout_per_call
                        )
                    else:
                        # Run sync function in thread pool
                        result = await asyncio.wait_for(
                            asyncio.get_event_loop().run_in_executor(
                                None, lambda: tool_func(**arguments)
                            ),
                            timeout=self.timeout_per_call
                        )

                    execution_time = (time.time() - start_time) * 1000

                    return ToolResult(
                        tool_call_id=call_id,
                        tool_name=tool_name,
                        result=result,
                        success=True,
                        execution_time_ms=execution_time,
                    )

            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.timeout_per_call}s"
                logger.warning(f"Tool {tool_name} timed out (attempt {attempt + 1})")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Tool {tool_name} failed (attempt {attempt + 1}): {e}")

            # Exponential backoff before retry
            if attempt < self.retry_attempts - 1:
                await asyncio.sleep(self.retry_delay * (2 ** attempt))

        # All retries failed
        return ToolResult(
            tool_call_id=call_id,
            tool_name=tool_name,
            result=None,
            success=False,
            error=last_error or "Unknown error",
        )

    def execute_batch_sync(
        self,
        tool_calls: List[Dict[str, Any]],
        tool_map: Dict[str, Callable],
    ) -> BatchResult:
        """
        Synchronous wrapper for execute_batch.

        Args:
            tool_calls: List of tool call dictionaries
            tool_map: Dictionary mapping tool names to functions

        Returns:
            BatchResult with all execution results
        """
        return asyncio.run(self.execute_batch(tool_calls, tool_map))


# =============================================================================
# Utility Functions
# =============================================================================


def extract_tool_calls(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract tool calls from an API response.

    Args:
        response: API response dictionary

    Returns:
        List of tool call dictionaries
    """
    choices = response.get("choices", [])
    if not choices:
        return []

    message = choices[0].get("message", {})
    return message.get("tool_calls", [])


def has_tool_calls(response: Dict[str, Any]) -> bool:
    """Check if response contains tool calls."""
    return len(extract_tool_calls(response)) > 0
