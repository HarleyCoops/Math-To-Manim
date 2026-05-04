# Kimi K2 Thinking Model Refactor

This folder contains a refactored version of the Math-To-Manim pipeline that uses the **Kimi K2 thinking model** from Moonshot AI instead of Claude.

## Overview

The Kimi K2 model uses an OpenAI-compatible API format, making it easier to integrate. However, we need to handle the case where tool calling may not be available or enabled. This refactor:

1. **Sets up Kimi K2 API client** - OpenAI-compatible wrapper
2. **Creates tool adapters** - Converts tool calls to verbose instructions when tools aren't available
3. **Refactors agents** - Adapts existing agents to work with Kimi K2

## Current Implementation Status

### Completed Components

- **KimiClient** (`kimi_client.py`): Fully implemented OpenAI-compatible API wrapper
  - Singleton pattern for efficient client reuse
  - Normalized response format
  - Tool call detection and extraction
  - Comprehensive error handling with helpful authentication messages
  
- **ToolAdapter** (`tool_adapter.py`): Complete tool-to-instruction converter
  - Converts tool schemas to natural language instructions
  - Handles both OpenAI format and custom formats
  - Creates enhanced prompts with tool context
  - Supports fallback when tools aren't available

- **KimiPrerequisiteExplorer** (`agents/prerequisite_explorer_kimi.py`): Fully functional agent
  - Builds knowledge trees by exploring prerequisite concepts
  - Foundation concept detection
  - In-memory caching to reduce API calls
  - Recursive tree exploration with depth limits
  - Same interface as Claude version for compatibility

- **KimiEnrichmentPipeline** (`agents/enrichment_chain.py`): Complete enrichment chain
  - **KimiMathematicalEnricher**: Adds equations, definitions, examples, and interpretations to each node
  - **KimiVisualDesigner**: Plans Manim visual specifications (elements, colors, animations, transitions)
  - **KimiNarrativeComposer**: Composes long-form narrative prompts (2000+ words) stitching all concepts together
  - Uses Moonshot's tool-calling interface for structured data extraction
  - Mirrors Claude pipeline stages while relying solely on OpenAI-compatible function calling

- **Enrichment CLI** (`examples/run_enrichment_pipeline.py`): Command-line helper
  - Loads existing knowledge tree JSON files
  - Runs the full enrichment pipeline end-to-end
  - Saves enriched tree with equations, visual specs, and narrative
  - Exports narrative prompt as separate text file

- **Configuration System** (`config.py`): Environment-based configuration
  - API key management
  - Model selection
  - Tool enable/disable flags
  - Thinking mode configuration

### Test Coverage

The implementation includes **15 comprehensive tests** across 3 test classes:

**TestKimiPrerequisiteExplorer** (9 tests):
- Foundation detection for basic concepts (addition, velocity, distance, time)
- Foundation detection for advanced concepts (quantum field theory, differential geometry)
- Prerequisite discovery functionality
- Knowledge tree building
- Tree serialization to JSON
- Cycle detection (ensures no circular dependencies)
- Depth monotonicity verification
- Max depth limit enforcement
- Caching mechanism validation

**TestKimiClient** (4 tests):
- Basic API call functionality
- Text content extraction from responses
- Tool call detection
- Tool call extraction

**TestKimiErrorHandling** (2 tests):
- Max depth exceeded handling
- Empty/invalid input handling

**Running Tests:**
```bash
# Run all Kimi K2 tests (requires MOONSHOT_API_KEY)
pytest tests/test_kimi_k2_prerequisite_explorer.py -v

# Run tests without API calls (unit tests only)
pytest tests/test_kimi_k2_prerequisite_explorer.py -v -k "not test_basic_api_call and not test_foundation and not test_discover and not test_explore"
```

**Note:** Tests marked with `@pytest.mark.skipif` require `MOONSHOT_API_KEY` to be set. Tests will skip gracefully if the key is not available.

## Structure

```
KimiK2Thinking/
├── README.md                    # This file
├── kimi_client.py               # Kimi K2 API client wrapper
├── tool_adapter.py              # Tool call to verbose instruction converter
├── agents/                      # Refactored agents
│   ├── __init__.py
│   ├── prerequisite_explorer_kimi.py
│   └── enrichment_chain.py     # Mathematical, visual, and narrative enrichment
├── examples/                    # Example usage scripts
│   ├── test_kimi_integration.py
│   └── run_enrichment_pipeline.py  # CLI for running enrichment pipeline
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

### Enrichment Pipeline Usage

Run the full enrichment chain on an existing knowledge tree:

```python
from KimiK2Thinking.agents.enrichment_chain import KimiEnrichmentPipeline
from KimiK2Thinking.agents.prerequisite_explorer_kimi import KnowledgeNode
import asyncio

async def main():
    # Load existing tree (or create one with PrerequisiteExplorer)
    tree = KnowledgeNode(...)  # Your knowledge tree
    
    # Run enrichment pipeline
    pipeline = KimiEnrichmentPipeline()
    result = await pipeline.run_async(tree)
    
    # Access enriched data
    print(f"Narrative: {result.narrative.verbose_prompt}")
    print(f"Total duration: {result.narrative.total_duration}s")
    
    # Tree nodes now have equations, visual_spec, and narrative populated
    for node in tree.prerequisites:
        print(f"{node.concept}: {len(node.equations)} equations")

asyncio.run(main())
```

### Command-Line Usage

Run the enrichment pipeline from the command line:

```bash
# Run enrichment on an existing tree JSON file
python KimiK2Thinking/examples/run_enrichment_pipeline.py path/to/tree.json

# This will:
# 1. Load the tree JSON
# 2. Run mathematical enrichment (adds equations/definitions)
# 3. Run visual design (adds Manim specs)
# 4. Compose narrative (creates long-form prompt)
# 5. Save enriched tree back to JSON
# 6. Export narrative to _narrative.txt file
```

See `examples/test_kimi_integration.py` for basic API examples.

## How It Works

### Architecture Overview

The implementation follows a three-layer architecture:

1. **Client Layer**: `KimiClient` handles all API communication
2. **Adapter Layer**: `ToolAdapter` converts tools to instructions when needed
3. **Agent Layer**: `KimiPrerequisiteExplorer` orchestrates the knowledge tree building

### Request Flow

The following TikZ diagram illustrates how a prerequisite exploration request flows through the system:

```tikz
\begin{tikzpicture}[node distance=1.5cm, auto]
  % Nodes
  \node[rectangle, draw, fill=blue!20] (agent) {Agent};
  \node[rectangle, draw, fill=green!20, below of=agent] (cache) {Cache Check};
  \node[rectangle, draw, fill=yellow!20, below of=cache] (tool) {Tool Check};
  \node[rectangle, draw, fill=orange!20, below left=1cm and 1cm of tool] (verbose) {Verbose Mode};
  \node[rectangle, draw, fill=orange!20, below right=1cm and 1cm of tool] (toolcall) {Tool Call Mode};
  \node[rectangle, draw, fill=red!20, below of=verbose] (client1) {KimiClient};
  \node[rectangle, draw, fill=red!20, below of=toolcall] (client2) {KimiClient};
  \node[rectangle, draw, fill=purple!20, below of=client1] (api1) {Moonshot API};
  \node[rectangle, draw, fill=purple!20, below of=client2] (api2) {Moonshot API};
  
  % Edges
  \draw[->] (agent) -- (cache);
  \draw[->] (cache) -- node[right] {Not cached} (tool);
  \draw[->] (tool) -- node[left] {Tools disabled} (verbose);
  \draw[->] (tool) -- node[right] {Tools enabled} (toolcall);
  \draw[->] (verbose) -- (client1);
  \draw[->] (toolcall) -- (client2);
  \draw[->] (client1) -- (api1);
  \draw[->] (client2) -- (api2);
\end{tikzpicture}
```

### Knowledge Tree Building Process

The prerequisite explorer builds knowledge trees recursively:

```tikz
\begin{tikzpicture}[level distance=2cm, level 1/.style={sibling distance=3cm}, level 2/.style={sibling distance=2cm}]
  \node[circle, draw] {Root Concept}
    child {
      node[circle, draw] {Prereq 1}
      child { node[circle, draw, fill=green!30] {Foundation} }
      child { node[circle, draw] {Sub-prereq} }
    }
    child {
      node[circle, draw] {Prereq 2}
      child { node[circle, draw, fill=green!30] {Foundation} }
    }
    child {
      node[circle, draw, fill=green!30] {Foundation}
    };
\end{tikzpicture}
```

### Tool Handling Strategy

When tools are available vs. when they're not:

```tikz
\begin{tikzpicture}[node distance=2cm, auto]
  \node[rectangle, draw] (start) {Agent Request};
  \node[rectangle, draw, below of=start] (check) {Tools Available?};
  \node[rectangle, draw, below left=1cm and 1.5cm of check] (yes) {Use Tools};
  \node[rectangle, draw, below right=1cm and 1.5cm of check] (no) {Convert to Instructions};
  \node[rectangle, draw, below of=yes] (api1) {API Call};
  \node[rectangle, draw, below of=no] (api2) {API Call};
  
  \draw[->] (start) -- (check);
  \draw[->] (check) -- node[left] {Yes} (yes);
  \draw[->] (check) -- node[right] {No} (no);
  \draw[->] (yes) -- (api1);
  \draw[->] (no) -- (api2);
\end{tikzpicture}
```

### Implementation Details

#### 1. KimiClient (`kimi_client.py`)

The client wraps the OpenAI SDK to communicate with Moonshot AI's API:

- **Initialization**: Reads API key from environment, configures base URL
- **Request Formatting**: Converts messages to OpenAI-compatible format
- **Response Normalization**: Extracts content, tool calls, and usage stats
- **Error Handling**: Provides detailed error messages for authentication failures

Key methods:
- `chat_completion()`: Main API call method
- `get_text_content()`: Extract text from response
- `has_tool_calls()`: Check if response contains tool calls
- `get_tool_calls()`: Extract tool call information

#### 2. ToolAdapter (`tool_adapter.py`)

Converts tool definitions into natural language instructions:

- **Tool Schema Parsing**: Extracts name, description, and parameters
- **Instruction Generation**: Creates detailed instructions for each tool
- **Prompt Enhancement**: Adds tool context to base prompts
- **Format Conversion**: Handles multiple tool definition formats

Key methods:
- `tool_to_instruction()`: Convert single tool to instruction
- `tools_to_instructions()`: Convert multiple tools
- `create_verbose_prompt()`: Enhance prompt with tool instructions
- `convert_tool_schema_to_openai_format()`: Normalize tool format

#### 3. KimiPrerequisiteExplorer (`agents/prerequisite_explorer_kimi.py`)

The main agent that builds knowledge trees:

**Exploration Process:**
1. Check cache for existing prerequisites
2. Determine if concept is foundational (no prerequisites needed)
3. If not foundational, discover prerequisites via API call
4. Recursively explore each prerequisite
5. Build tree structure with depth tracking

**Foundation Detection:**
- Uses specialized prompt to determine if concept is foundational
- Foundation concepts are high school level or below
- Stops recursion at foundation concepts

**Caching Strategy:**
- In-memory cache stores discovered prerequisites
- Reduces redundant API calls for same concepts
- Cache persists for duration of explorer instance

**Tree Structure:**
- `KnowledgeNode` dataclass represents each concept
- Each node contains: concept name, depth, foundation flag, prerequisites list
- Supports serialization to JSON for persistence

#### 4. KimiEnrichmentPipeline (`agents/enrichment_chain.py`)

The enrichment chain adds mathematical content, visual specifications, and narrative to knowledge trees:

**MathematicalEnricher:**
- Uses `write_mathematical_content` tool to extract structured data
- Adds LaTeX equations (2-5 per concept, formatted for MathTex)
- Provides symbol definitions dictionary
- Includes interpretation, examples, and typical values
- Adapts complexity based on foundation status (high school vs. upper-undergraduate)

**VisualDesigner:**
- Uses `design_visual_plan` tool for structured visual specifications
- Plans Manim elements (MathTex, VGroup, Axes, etc.)
- Defines color palettes using Manim color constants
- Outlines animation sequences and transitions
- Maintains continuity with previous scenes
- Estimates duration per scene (10-40 seconds)

**NarrativeComposer:**
- Uses `compose_narrative` tool to generate long-form prompts
- Orders concepts topologically (foundations first)
- Integrates equations, visual specs, and transitions
- Creates 2000+ word narrative prompt
- Includes pacing and timing suggestions
- Writes final narrative to root node

**Tool Call Extraction:**
- `_extract_tool_payload()`: Extracts JSON from tool call arguments
- `_parse_json_fallback()`: Fallback parser for raw JSON responses
- Handles both tool calls and plain JSON responses gracefully

**Pipeline Flow:**
1. Mathematical enrichment runs recursively through tree
2. Visual design runs with parent context for continuity
3. Narrative composition runs once on complete enriched tree
4. All stages use Moonshot's tool-calling interface for structured data

### Error Handling

The implementation includes comprehensive error handling:

- **API Errors**: Authentication failures provide detailed troubleshooting steps
- **Parse Errors**: Multiple fallback strategies for parsing JSON responses
- **Tool Errors**: Graceful fallback from tool mode to verbose mode
- **Depth Limits**: Prevents infinite recursion with max_depth parameter

### Performance Considerations

- **Singleton Client**: Reuses API client instance across requests
- **Caching**: Reduces redundant API calls for repeated concepts
- **Async Support**: Uses async/await for concurrent operations
- **Depth Limiting**: Prevents excessive API calls with depth limits
- **Structured Tool Calls**: Tool-calling interface provides reliable JSON extraction without parsing
- **Sequential Pipeline**: Enrichment stages run sequentially to maintain data dependencies

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

