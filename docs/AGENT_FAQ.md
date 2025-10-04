# Agent FAQ - Quick Answers for Beginners

**Created**: 2025-10-04
**Audience**: Developers new to AI agents

---

## What exactly is an "agent"?

**Simple answer**: An agent is AI that can use tools and make decisions autonomously.

**In your current code**: You have "conceptual agents" - Python classes that encapsulate specific reasoning tasks (ConceptAnalyzer, PrerequisiteExplorer). They're called "agents" because they have specific responsibilities, but they're just making API calls to Claude.

**True agent** (future): AI that can:
- Call tools (web search, file operations, code execution)
- Make multi-step decisions
- Retry when things fail
- Remember conversation context automatically

---

## What's the difference between what I have now vs. a "real" agent SDK?

### What You Have Now (Basic Anthropic SDK)

```python
from anthropic import Anthropic

client = Anthropic(api_key=...)
response = client.messages.create(
    model="claude-sonnet-4.5-20251022",
    messages=[{"role": "user", "content": "What are the prerequisites for cosmology?"}]
)

answer = response.content[0].text  # Done!
```

**Characteristics**:
- [DONE] Simple, predictable
- [DONE] Easy to debug
- [FAIL] Single turn only
- [FAIL] No tools
- [FAIL] You handle all logic

### What Claude Agent SDK Adds

```python
from claude_agent_sdk import Agent, tools

agent = Agent(
    model="claude-sonnet-4.5-20251022",
    tools=[tools.web_search, tools.file_read, tools.code_execution]
)

result = agent.run("Find prerequisites for cosmology and validate against MIT's curriculum")

# Agent automatically:
# - Searches web for MIT curriculum
# - Reads local files if needed
# - Asks follow-up questions
# - Retries if tools fail
# - Manages context window
```

**Characteristics**:
- [DONE] Multi-step reasoning
- [DONE] Tool access
- [DONE] Automatic error handling
- [WARNING] More complex
- [WARNING] Less predictable

---

## So why do my files say "Claude Agent SDK" if I'm not using it?

**Good catch!** The documentation was aspirational/future-looking. Here's the reality:

**Currently using**:
- `anthropic` package (basic API client)
- Manual tool orchestration (you write the logic)

**Plan to use**:
- `claude-agent-sdk` package (adds autonomy)
- Automatic tool orchestration (SDK handles it)

**When to upgrade**: After you've mastered the basics and need multi-turn reasoning with tools.

---

## How do I see what my agents are actually doing?

### Method 1: Run the Inspector (Easiest)

```bash
python inspect_agents.py
```

This will show you:
- Every API call made
- Input/output for each call
- Time taken
- Order of operations

### Method 2: Add Print Statements

```python
# In prerequisite_explorer_claude.py

def discover_prerequisites(self, concept: str):
    print(f"\n[SEARCH] Discovering prerequisites for: {concept}")

    response = client.messages.create(...)

    print(f"[DONE] Found: {response.content[0].text}")

    return prerequisites
```

### Method 3: Check the Logs File

After running `inspect_agents.py`, check `agent_inspection_demo.json` for detailed logs.

---

## What tools do my agents currently have access to?

**None.** Your agents can only:
- Send text to Claude
- Receive text responses
- Parse JSON

They **cannot**:
- Search the web
- Read/write files (besides what YOU code explicitly)
- Execute code
- Use databases

**To add tools**: Upgrade to `claude-agent-sdk` or integrate with LangChain.

---

## How do I inspect which agents are available?

Your "agents" are just Python classes. To see what's available:

```python
# List all agent classes
from prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer

agents = [ConceptAnalyzer, PrerequisiteExplorer]

for agent_class in agents:
    print(f"Agent: {agent_class.__name__}")
    print(f"Purpose: {agent_class.__doc__}")
    print(f"Methods: {[m for m in dir(agent_class) if not m.startswith('_')]}")
    print()
```

Output:
```
Agent: ConceptAnalyzer
Purpose: Analyzes user input to extract the core concept and metadata.
Methods: ['analyze', 'model']

Agent: PrerequisiteExplorer
Purpose: Core agent that recursively discovers prerequisites for any concept.
Methods: ['cache', 'discover_prerequisites', 'explore', 'is_foundation', 'max_depth', 'model']
```

---

## How can I verify agents are doing what I think they're doing?

### 1. Read the Prompts

The most important thing is seeing what you're actually asking Claude:

```python
# In prerequisite_explorer_claude.py, add this to is_foundation():

def is_foundation(self, concept: str) -> bool:
    system_prompt = """You are an expert educator..."""
    user_prompt = f'Is "{concept}" a foundational concept?'

    # ADD THIS:
    print("\n" + "="*70)
    print("SYSTEM PROMPT:")
    print(system_prompt)
    print("\nUSER PROMPT:")
    print(user_prompt)
    print("="*70)

    response = client.messages.create(...)

    # AND THIS:
    print("\nRESPONSE:")
    print(response.content[0].text)
    print("="*70 + "\n")

    return response.content[0].text.strip().lower().startswith('yes')
```

### 2. Count API Calls

```python
# Track how many times you're calling Claude

call_count = 0

original_create = client.messages.create

def tracked_create(*args, **kwargs):
    global call_count
    call_count += 1
    print(f"[API CALL #{call_count}]")
    return original_create(*args, **kwargs)

client.messages.create = tracked_create

# Now run your agent
explorer = PrerequisiteExplorer()
tree = explorer.explore("cosmology")

print(f"\nTotal API calls: {call_count}")
```

### 3. Validate Output

```python
# After building a knowledge tree, verify it's correct

def validate_tree(node, visited=None):
    """Check tree for issues"""
    if visited is None:
        visited = set()

    issues = []

    # Check for cycles
    if node.concept in visited:
        issues.append(f"CYCLE DETECTED: {node.concept}")
    visited.add(node.concept)

    # Check depth makes sense
    for prereq in node.prerequisites:
        if prereq.depth <= node.depth:
            issues.append(f"INVALID DEPTH: {prereq.concept} should be deeper than {node.concept}")

    # Recurse
    for prereq in node.prerequisites:
        issues.extend(validate_tree(prereq, visited))

    return issues

# Use it
tree = explorer.explore("cosmology")
problems = validate_tree(tree)

if problems:
    print("[WARNING] ISSUES FOUND:")
    for problem in problems:
        print(f"  - {problem}")
else:
    print("[DONE] Tree is valid!")
```

---

## When should I upgrade to the full Agent SDK?

Upgrade when you need:

1. **Tool calling** - Web search, file ops, code execution
2. **Multi-turn conversations** - Agent asks follow-up questions
3. **Error recovery** - Automatic retries when tools fail
4. **Context management** - Long conversations without manual truncation

**Don't upgrade** if:
- Current setup works fine
- You're still learning the basics
- You want predictable behavior
- You're on a tight budget (more API calls = more cost)

---

## Quick Start: Inspect Your Agents Right Now

```bash
# 1. Run the inspector
python inspect_agents.py

# 2. Inspect a specific concept
python inspect_agents.py --concept "special relativity" 3

# 3. Check the logs
cat agent_inspection_demo.json

# 4. View in Python
python
>>> import json
>>> with open('agent_inspection_demo.json') as f:
...     logs = json.load(f)
>>> print(f"Total calls: {len(logs)}")
>>> print(f"First call: {logs[0]['method_name']}")
```

---

## Further Reading

- **Full Guide**: [docs/AGENT_INSPECTION_GUIDE.md](docs/AGENT_INSPECTION_GUIDE.md)
- **Anthropic Tool Use**: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- **Agent Building**: https://docs.anthropic.com/en/docs/agents
- **Claude Agent SDK Docs**: https://docs.claude.com/en/api/agent-sdk/overview

---

**Last Updated**: 2025-10-04
**Maintainer**: @HarleyCoops
