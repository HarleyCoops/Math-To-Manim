# Kimi K2 Refactor Architecture

## Overview

This refactor maintains the same agent interfaces as the Claude implementation while using the Kimi K2 thinking model from Moonshot AI. The key challenge is handling tool calls when tools may not be available.

## Architecture Components

### 1. KimiClient (`kimi_client.py`)

**Purpose**: Wrapper around OpenAI-compatible API for Moonshot AI

**Key Features**:
- OpenAI-compatible interface (uses `openai` package)
- Normalized response format
- Tool call detection and extraction
- Singleton pattern for efficiency

**Usage**:
```python
client = KimiClient()
response = client.chat_completion(messages=[...], tools=[...])
```

### 2. ToolAdapter (`tool_adapter.py`)

**Purpose**: Convert tool definitions to verbose instructions

**Key Features**:
- Converts tool schemas to natural language instructions
- Handles both OpenAI format and custom formats
- Creates enhanced prompts with tool context

**Why Needed**:
- Kimi K2 may not support all tool calling features
- Some deployments may disable tools
- Provides fallback mechanism

**Example**:
```python
adapter = ToolAdapter()
# Tool definition -> verbose instruction
instruction = adapter.tool_to_instruction(tool_def)
# Enhanced prompt with tool context
prompt = adapter.create_verbose_prompt(base_prompt, tools=[tool_def])
```

### 3. Refactored Agents (`agents/`)

**Pattern**: Same interface as Claude versions

**Key Design Decisions**:

1. **Tool Handling Strategy**:
   ```python
   if self.use_tools and self.tools:
       # Try with tools first
       try:
           response = client.chat_completion(..., tools=self.tools)
           if client.has_tool_calls(response):
               # Handle tool calls
       except:
           # Fallback to verbose instructions
           response = self._get_verbose_response(...)
   else:
       # Use verbose instructions directly
       response = self._get_verbose_response(...)
   ```

2. **Cache Compatibility**:
   - Same in-memory cache structure
   - Same KnowledgeNode dataclass
   - Same tree structure

3. **Error Handling**:
   - Graceful fallback from tools to verbose
   - Same exception handling patterns
   - Compatible error messages

## Tool Call Conversion Flow

```
┌─────────────────┐
│  Agent Request  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Check Tools     │
│  Available?      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────────┐
│ Use     │ │ Convert Tools to  │
│ Tools   │ │ Verbose           │
│         │ │ Instructions      │
└────┬────┘ └────────┬──────────┘
     │                │
     │                │
     └───────┬────────┘
             │
             ▼
      ┌──────────────┐
      │  API Call    │
      │  (Kimi K2)   │
      └──────┬───────┘
             │
             ▼
      ┌──────────────┐
      │  Parse       │
      │  Response    │
      └──────────────┘
```

## Key Differences from Claude Implementation

| Aspect | Claude | Kimi K2 |
|--------|--------|---------|
| **API Client** | `anthropic.Anthropic` | `openai.OpenAI` (Moonshot endpoint) |
| **API Format** | `messages.create()` | `chat.completions.create()` |
| **Tool Format** | MCP tools | OpenAI function calling |
| **Response Format** | `response.content[0].text` | `response.choices[0].message.content` |
| **Tool Calls** | `response.stop_reason == "tool_use"` | `message.tool_calls` array |
| **Thinking Mode** | Built-in | Via API parameters |

## Migration Strategy

### Phase 1: Core Infrastructure
- [x] KimiClient implementation
- [x] ToolAdapter implementation
- [x] Configuration system

### Phase 2: Agent Refactoring
- [x] PrerequisiteExplorer refactored
- [ ] VisualDesigner refactored
- [ ] MathematicalEnricher refactored
- [ ] NarrativeComposer refactored
- [ ] Other agents...

### Phase 3: Testing & Validation
- [ ] Unit tests for KimiClient
- [ ] Unit tests for ToolAdapter
- [ ] Integration tests for agents
- [ ] Comparison tests (Claude vs Kimi)

### Phase 4: Documentation
- [x] README
- [x] SETUP guide
- [x] Architecture doc
- [ ] API reference
- [ ] Migration guide

## Tool Conversion Examples

### Example 1: Cache Tool

**Original Tool Call**:
```python
tool_call = {
    "name": "get_cached_prerequisites",
    "arguments": {"concept": "quantum mechanics"}
}
```

**Converted to Instruction**:
```
Please perform the action 'get_cached_prerequisites' with the following parameters:
  - concept: quantum mechanics

If you have cached prerequisites for this concept, use them. Otherwise, 
provide the prerequisites directly based on your knowledge.
```

### Example 2: Validation Tool

**Original Tool Call**:
```python
tool_call = {
    "name": "validate_latex",
    "arguments": {"latex_code": "\\frac{a}{b}"}
}
```

**Converted to Instruction**:
```
Please validate the LaTeX code: \frac{a}{b}

Check for:
- Unmatched delimiters ($, \[, \])
- Common syntax errors
- Proper escaping

Provide validation results in your response.
```

## Best Practices

1. **Always provide fallback**: Don't assume tools are available
2. **Use verbose instructions**: Make them detailed enough to replace tool functionality
3. **Maintain compatibility**: Keep same interfaces as Claude versions
4. **Test both modes**: Test with tools enabled and disabled
5. **Document tool conversions**: Keep track of how tools are converted

## Future Enhancements

1. **Tool execution**: Actually execute tools when available
2. **Hybrid mode**: Use tools when available, verbose when not
3. **Tool registry**: Centralized tool definitions
4. **Performance monitoring**: Track tool vs verbose performance
5. **Automatic conversion**: Auto-generate verbose instructions from tool schemas

