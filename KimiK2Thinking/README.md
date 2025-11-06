# Kimi K2 Thinking Model Refactor

This folder contains a refactored version of the Math-To-Manim pipeline that uses the **Kimi K2 thinking model** from Moonshot AI instead of Claude.

## Overview

The Kimi K2 model uses an OpenAI-compatible API format, making it easier to integrate. However, we need to handle the case where tool calling may not be available or enabled. This refactor:

1. **Sets up Kimi K2 API client** - OpenAI-compatible wrapper
2. **Creates tool adapters** - Converts tool calls to verbose instructions when tools aren't available
3. **Refactors agents** - Adapts existing agents to work with Kimi K2

## Structure

```
KimiK2Thinking/
├── README.md                    # This file
├── kimi_client.py               # Kimi K2 API client wrapper
├── tool_adapter.py              # Tool call to verbose instruction converter
├── agents/                      # Refactored agents
│   ├── __init__.py
│   ├── prerequisite_explorer_kimi.py
│   └── ... (other agents)
├── examples/                    # Example usage scripts
│   └── test_kimi_integration.py
└── config.py                    # Configuration and constants
```

## Setup

1. **Get API Key**: Register at https://platform.moonshot.ai/ and get your API key

2. **Set Environment Variable**: Add to your `.env` file in the project root:
   ```bash
   MOONSHOT_API_KEY=your_api_key_here
   KIMI_MODEL=moonshot-v1-8k  # Optional: specify model name
   KIMI_USE_TOOLS=true        # Optional: enable/disable tools
   KIMI_ENABLE_THINKING=true   # Optional: enable thinking mode
   ```

3. **Install Dependencies**: The Kimi API is OpenAI-compatible, so we use the `openai` package:
   ```bash
   pip install openai python-dotenv
   ```

4. **Verify Setup**: Run the test script:
   ```bash
   python KimiK2Thinking/examples/test_kimi_integration.py
   ```

## Key Differences from Claude Implementation

### 1. API Format
- **Claude**: Uses `anthropic` SDK with `messages.create()`
- **Kimi K2**: Uses OpenAI-compatible format with `chat.completions.create()`

### 2. Tool Handling
- **With Tools**: Kimi K2 can use function calling (similar to OpenAI)
- **Without Tools**: We convert tool calls to verbose natural language instructions in prompts

### 3. Thinking Mode
- Kimi K2 has a "thinking" mode that shows reasoning steps
- This is similar to Claude's thinking but uses different API parameters

## Usage

### Basic Usage

```python
from KimiK2Thinking.agents.prerequisite_explorer_kimi import KimiPrerequisiteExplorer
import asyncio

async def main():
    explorer = KimiPrerequisiteExplorer(max_depth=3, use_tools=True)
    tree = await explorer.explore_async("quantum field theory", verbose=True)
    tree.print_tree()

asyncio.run(main())
```

### Direct API Usage

```python
from KimiK2Thinking.kimi_client import KimiClient

client = KimiClient()
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=100
)
print(client.get_text_content(response))
```

### Tool Adapter Usage

When tools aren't available, the adapter converts them to verbose instructions:

```python
from KimiK2Thinking.tool_adapter import ToolAdapter

adapter = ToolAdapter()
tools = [...]  # Your tool definitions
instructions = adapter.tools_to_instructions(tools)
# Use instructions in your prompt
```

See `examples/test_kimi_integration.py` for a complete example.

## Migration Notes

- All agents maintain the same interface as the Claude versions
- Tool calls are automatically converted to verbose instructions if tools aren't available
- The API responses may have slightly different structure, but we normalize them

## References

- [Moonshot AI Platform](https://platform.moonshot.ai/)
- [Kimi K2 Documentation](https://platform.moonshot.ai/docs/guide/use-kimi-k2-thinking-model)

## Future Development

### Options

- Build an MCP server that wraps Kimi’s OpenAI-compatible API; expose `chat.completions.create` as an MCP tool, add optional subtools for saved caches, etc., then register the server in your IDE’s MCP client.
- Stand up a thin HTTP proxy that converts MCP tool invocations into Moonshot REST calls; useful if you already have a proxy layer for Claude/OpenAI.
- Use a CLI bridge: write a small script that accepts MCP “tool” JSON on stdin, forwards it to Kimi, and returns the completion—handy for smoke tests without wiring a full server.

### Next Steps

- Decide which MCP client you want to target (Cursor, VS Code, custom CLI) so the transport protocol is clear.
- Scaffold a simple MCP server (e.g., Python + `anthropic-mcp` or Node + `@modelcontextprotocol/sdk`) and plug in the existing `KimiClient`.
- Test with a single `chat` tool, then expand to match the tool-adapter behavior if it proves stable.

