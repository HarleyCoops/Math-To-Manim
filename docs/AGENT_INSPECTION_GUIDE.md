# Agent Inspection & Development Guide

**Created**: 2025-10-04
**Purpose**: Understand what agents are, how they work, and how to inspect them in Math-To-Manim

---

## Important: What You're Actually Using

### Current Setup (As Of Now)

You're using the **Anthropic Python SDK** (`anthropic` package), which is the basic API client for making calls to Claude. You're **not yet** using a full agent framework.

**What you have**:
```python
from anthropic import Anthropic  # ← Basic API client

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(...)  # ← Simple API call
```

**What an agent framework would add**:
- Tool calling (file operations, code execution, web search)
- Context management (automatic compaction)
- Multi-step reasoning loops
- Error handling and retries
- Session persistence

---

## Understanding Agents vs. Simple API Calls

### Simple API Call (What You Have Now)

```python
# prerequisite_explorer_claude.py
def discover_prerequisites(self, concept: str) -> List[str]:
    """Ask Claude once, get response, done."""

    response = client.messages.create(
        model="claude-sonnet-4.5-20251022",
        max_tokens=500,
        messages=[{"role": "user", "content": f"Prerequisites for {concept}?"}]
    )

    return json.loads(response.content[0].text)
```

**Characteristics**:
- [DONE] Simple, predictable
- [DONE] Easy to debug
- [FAIL] Single turn (no follow-up questions)
- [FAIL] No tool access
- [FAIL] Manual context management

### Agent Framework (Future)

```python
# With Claude Agent SDK (future implementation)
from claude_agent_sdk import Agent, tools

agent = Agent(
    name="PrerequisiteExplorer",
    model="claude-sonnet-4.5-20251022",
    tools=[tools.web_search, tools.file_read, tools.code_execution],
    max_iterations=10
)

result = agent.run(
    "Find prerequisites for cosmology and validate against university syllabi"
)
# Agent can:
# - Search the web for curriculum data
# - Read local files with concept definitions
# - Execute Python to analyze the data
# - Ask follow-up questions autonomously
```

**Characteristics**:
- [DONE] Multi-turn reasoning
- [DONE] Tool access (web, files, code)
- [DONE] Automatic context management
- [WARNING] More complex to debug
- [WARNING] Non-deterministic behavior

---

## What Are "Agents" in Your Current Code?

In your codebase, "agents" are **conceptual components** - Python classes that encapsulate specific reasoning tasks:

### 1. ConceptAnalyzer "Agent"

**Location**: `prerequisite_explorer_claude.py` (lines 223-297)

**What it does**: Parses user input to extract core concept, domain, level

**Inspection**:
```python
from prerequisite_explorer_claude import ConceptAnalyzer

# Create instance
analyzer = ConceptAnalyzer(model="claude-sonnet-4.5-20251022")

# Test it
result = analyzer.analyze("Explain cosmology to me")
print(json.dumps(result, indent=2))

# Output:
# {
#   "core_concept": "cosmology",
#   "domain": "physics/astronomy",
#   "level": "beginner",
#   "goal": "Understand how the universe evolved..."
# }
```

**How it works internally**:
1. Takes user input string
2. Constructs a system prompt with instructions
3. Calls Claude API once
4. Parses JSON response
5. Returns structured data

### 2. PrerequisiteExplorer "Agent"

**Location**: `prerequisite_explorer_claude.py` (lines 62-221)

**What it does**: Recursively discovers prerequisites for concepts

**Inspection**:
```python
from prerequisite_explorer_claude import PrerequisiteExplorer

# Create instance
explorer = PrerequisiteExplorer(
    model="claude-sonnet-4.5-20251022",
    max_depth=3  # Limit recursion
)

# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test it
tree = explorer.explore("quantum mechanics")

# Watch the console output to see:
# - Each recursive call
# - API calls being made
# - Cache hits
# - Foundation detection

# Inspect the result
tree.print_tree()
print(f"\nTotal concepts discovered: {count_nodes(tree)}")
print(f"Foundation concepts: {count_foundations(tree)}")
```

**How it works internally**:
1. Checks if concept is foundational (API call #1)
2. If not, discovers prerequisites (API call #2)
3. Recursively explores each prerequisite (more API calls)
4. Caches results to avoid redundant calls
5. Returns tree structure

---

## How to Inspect What Your Agents Are Doing

### Method 1: Add Logging

```python
# prerequisite_explorer_claude.py

import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_activity.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PrerequisiteExplorer:
    def explore(self, concept: str, depth: int = 0) -> KnowledgeNode:
        logger.info(f"[DEPTH {depth}] Exploring concept: {concept}")

        # Log API calls
        logger.debug(f"Checking if '{concept}' is foundational...")
        is_foundation = self.is_foundation(concept)
        logger.debug(f"Result: {'YES' if is_foundation else 'NO'}")

        if is_foundation:
            logger.info(f"[DEPTH {depth}] {concept} is FOUNDATION - stopping")
            return KnowledgeNode(...)

        # Log prerequisite discovery
        logger.debug(f"Discovering prerequisites for '{concept}'...")
        prereqs = self.discover_prerequisites(concept)
        logger.info(f"[DEPTH {depth}] Found {len(prereqs)} prerequisites: {prereqs}")

        # Continue...
```

**View logs**:
```bash
# Real-time monitoring
tail -f agent_activity.log

# Filter for specific concept
grep "quantum mechanics" agent_activity.log

# Count API calls
grep "API CALL" agent_activity.log | wc -l
```

### Method 2: Add Metrics Collection

```python
# prerequisite_explorer_claude.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class AgentMetrics:
    """Track agent performance"""
    api_calls: int = 0
    cache_hits: int = 0
    concepts_explored: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0

    def log_api_call(self, tokens: int):
        self.api_calls += 1
        self.total_tokens += tokens
        # Claude Sonnet 4.5 pricing (example)
        self.total_cost += (tokens / 1000) * 0.003

class PrerequisiteExplorer:
    def __init__(self, model: str = CLAUDE_MODEL, max_depth: int = 4):
        self.model = model
        self.max_depth = max_depth
        self.cache = {}
        self.metrics = AgentMetrics()  # ← Add metrics

    def discover_prerequisites(self, concept: str) -> List[str]:
        # Check cache first
        if concept in self.cache:
            self.metrics.cache_hits += 1
            return self.cache[concept]

        # Make API call
        response = client.messages.create(...)

        # Track metrics
        self.metrics.log_api_call(
            response.usage.input_tokens + response.usage.output_tokens
        )

        return prerequisites

    def print_metrics(self):
        """Display agent performance"""
        print("\n" + "="*50)
        print("AGENT METRICS")
        print("="*50)
        print(f"Concepts explored: {self.metrics.concepts_explored}")
        print(f"API calls made: {self.metrics.api_calls}")
        print(f"Cache hits: {self.metrics.cache_hits}")
        print(f"Total tokens: {self.metrics.total_tokens:,}")
        print(f"Estimated cost: ${self.metrics.total_cost:.4f}")
        print(f"Cache efficiency: {self.metrics.cache_hits / max(1, self.metrics.api_calls) * 100:.1f}%")
        print("="*50)
```

**Usage**:
```python
explorer = PrerequisiteExplorer()
tree = explorer.explore("cosmology")
explorer.print_metrics()

# Output:
# ==================================================
# AGENT METRICS
# ==================================================
# Concepts explored: 23
# API calls made: 46
# Cache hits: 12
# Total tokens: 15,234
# Estimated cost: $0.0457
# Cache efficiency: 26.1%
# ==================================================
```

### Method 3: Trace API Calls

```python
# Create a wrapper to trace all Anthropic API calls

import functools
import json
from datetime import datetime

class APITracer:
    """Track all API calls with details"""

    def __init__(self, output_file="api_trace.json"):
        self.output_file = output_file
        self.calls = []

    def trace_call(self, func):
        """Decorator to trace API calls"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Record start time
            start_time = datetime.now()

            # Extract prompt info
            messages = kwargs.get('messages', [])
            system = kwargs.get('system', '')

            # Make the actual API call
            response = func(*args, **kwargs)

            # Record end time
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Save trace
            trace = {
                'timestamp': start_time.isoformat(),
                'duration_seconds': duration,
                'model': kwargs.get('model'),
                'system_prompt': system[:100] + '...',  # Truncate
                'user_message': messages[-1]['content'][:100] + '...',
                'response_preview': response.content[0].text[:100] + '...',
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }

            self.calls.append(trace)

            # Write to file
            with open(self.output_file, 'w') as f:
                json.dump(self.calls, f, indent=2)

            print(f"[API TRACE] Call #{len(self.calls)} - {duration:.2f}s - {trace['total_tokens']} tokens")

            return response

        return wrapper

# Use it
tracer = APITracer()

# Monkey-patch the client
original_create = client.messages.create
client.messages.create = tracer.trace_call(original_create)

# Now all API calls are traced!
explorer = PrerequisiteExplorer()
tree = explorer.explore("cosmology")

# View the trace
with open('api_trace.json') as f:
    trace_data = json.load(f)
    print(f"Total API calls: {len(trace_data)}")
    print(f"Total cost: ${sum(call['total_tokens'] for call in trace_data) * 0.000003:.4f}")
```

### Method 4: Visualize Agent Activity

```python
# Create a real-time visualization of agent exploration

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import defaultdict

class AgentVisualizer:
    """Real-time visualization of prerequisite exploration"""

    def __init__(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 5))
        self.depth_counts = defaultdict(int)
        self.api_calls_over_time = []

    def on_explore(self, concept: str, depth: int):
        """Called whenever a concept is explored"""
        self.depth_counts[depth] += 1
        self.api_calls_over_time.append(len(self.api_calls_over_time) + 1)

        # Update depth distribution
        self.ax1.clear()
        self.ax1.bar(self.depth_counts.keys(), self.depth_counts.values())
        self.ax1.set_xlabel('Depth')
        self.ax1.set_ylabel('Concepts')
        self.ax1.set_title('Prerequisite Tree Depth Distribution')

        # Update API calls over time
        self.ax2.clear()
        self.ax2.plot(self.api_calls_over_time)
        self.ax2.set_xlabel('Concept Number')
        self.ax2.set_ylabel('Cumulative API Calls')
        self.ax2.set_title('API Call Growth')

        plt.pause(0.01)

    def show(self):
        plt.show()

# Usage
visualizer = AgentVisualizer()

# Modify PrerequisiteExplorer to call visualizer
class PrerequisiteExplorer:
    def __init__(self, visualizer=None, **kwargs):
        self.visualizer = visualizer
        # ... rest of init

    def explore(self, concept: str, depth: int = 0):
        if self.visualizer:
            self.visualizer.on_explore(concept, depth)

        # ... rest of explore logic

# Run with visualization
explorer = PrerequisiteExplorer(visualizer=visualizer)
tree = explorer.explore("cosmology")
visualizer.show()
```

---

## Inspecting Agent Prompts

One of the most important things to understand is **what exactly you're asking Claude to do**.

### View Prompts in Real-Time

```python
# prerequisite_explorer_claude.py

class PrerequisiteExplorer:
    def is_foundation(self, concept: str) -> bool:
        system_prompt = """You are an expert educator..."""

        user_prompt = f'Is "{concept}" a foundational concept?\\n\\nAnswer with ONLY "yes" or "no".'

        # PRINT THE PROMPTS BEFORE SENDING
        print("\n" + "="*70)
        print("CALLING CLAUDE API: is_foundation()")
        print("="*70)
        print("SYSTEM PROMPT:")
        print(system_prompt)
        print("\nUSER PROMPT:")
        print(user_prompt)
        print("="*70)

        response = client.messages.create(
            model=self.model,
            max_tokens=10,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        answer = response.content[0].text

        # PRINT THE RESPONSE
        print("\nCLAUDE RESPONSE:")
        print(answer)
        print("="*70 + "\n")

        return answer.strip().lower().startswith('yes')
```

### Save All Prompts for Analysis

```python
class PromptLogger:
    """Log all prompts and responses for later analysis"""

    def __init__(self, output_dir="prompt_logs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.call_count = 0

    def log_interaction(self, system_prompt, user_prompt, response, metadata=None):
        """Save a single interaction"""
        self.call_count += 1

        log_entry = {
            'call_number': self.call_count,
            'timestamp': datetime.now().isoformat(),
            'system_prompt': system_prompt,
            'user_prompt': user_prompt,
            'response': response,
            'metadata': metadata or {}
        }

        filename = f"{self.output_dir}/call_{self.call_count:04d}.json"
        with open(filename, 'w') as f:
            json.dump(log_entry, f, indent=2)

        return filename

# Usage
prompt_logger = PromptLogger()

# In your agent
response = client.messages.create(...)
prompt_logger.log_interaction(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    response=response.content[0].text,
    metadata={'concept': concept, 'depth': depth}
)
```

---

## Testing Agents

### Unit Tests for Individual Agents

```python
# tests/test_prerequisite_explorer.py

import pytest
from prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer

class TestConceptAnalyzer:
    """Test the ConceptAnalyzer agent"""

    def setup_method(self):
        self.analyzer = ConceptAnalyzer()

    def test_simple_physics_question(self):
        """Test analyzing a basic physics question"""
        result = self.analyzer.analyze("Explain cosmology")

        assert result['core_concept'] == 'cosmology'
        assert result['domain'] in ['physics', 'physics/astronomy']
        assert result['level'] in ['beginner', 'intermediate']

    def test_advanced_math_question(self):
        """Test analyzing advanced mathematics"""
        result = self.analyzer.analyze("Prove the Riemann hypothesis")

        assert 'riemann' in result['core_concept'].lower()
        assert result['level'] == 'advanced'

    def test_output_structure(self):
        """Verify output always has required fields"""
        result = self.analyzer.analyze("What is calculus?")

        required_fields = ['core_concept', 'domain', 'level', 'goal']
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

class TestPrerequisiteExplorer:
    """Test the PrerequisiteExplorer agent"""

    def setup_method(self):
        self.explorer = PrerequisiteExplorer(max_depth=2)  # Limit for tests

    def test_foundation_detection(self):
        """Test that basic concepts are detected as foundations"""
        assert self.explorer.is_foundation("addition") == True
        assert self.explorer.is_foundation("velocity") == True
        assert self.explorer.is_foundation("quantum field theory") == False

    def test_prerequisite_discovery(self):
        """Test discovering prerequisites"""
        prereqs = self.explorer.discover_prerequisites("calculus")

        assert isinstance(prereqs, list)
        assert len(prereqs) > 0
        assert len(prereqs) <= 5  # Should be limited

    def test_caching(self):
        """Verify caching reduces API calls"""
        # First call
        tree1 = self.explorer.explore("algebra")
        calls_1 = self.explorer.metrics.api_calls

        # Second call (should use cache)
        tree2 = self.explorer.explore("algebra")
        calls_2 = self.explorer.metrics.api_calls

        assert calls_2 == calls_1, "Cache should prevent duplicate API calls"

    def test_tree_depth_limit(self):
        """Ensure max_depth is respected"""
        tree = self.explorer.explore("quantum mechanics")

        def check_depth(node, current_depth=0):
            assert current_depth <= self.explorer.max_depth
            for prereq in node.prerequisites:
                check_depth(prereq, current_depth + 1)

        check_depth(tree)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Integration Tests

```python
# tests/test_full_pipeline.py

def test_full_pipeline():
    """Test the complete flow: analyze -> explore -> build tree"""

    # Step 1: Analyze concept
    analyzer = ConceptAnalyzer()
    analysis = analyzer.analyze("Explain special relativity")

    # Step 2: Build prerequisite tree
    explorer = PrerequisiteExplorer(max_depth=3)
    tree = explorer.explore(analysis['core_concept'])

    # Step 3: Verify tree structure
    assert tree.concept == 'special relativity'
    assert len(tree.prerequisites) > 0

    # Step 4: Check that foundations are reached
    def has_foundations(node):
        if node.is_foundation:
            return True
        return any(has_foundations(p) for p in node.prerequisites)

    assert has_foundations(tree), "Tree should reach foundation concepts"

    # Step 5: Verify all nodes have valid data
    def validate_node(node):
        assert isinstance(node.concept, str)
        assert isinstance(node.depth, int)
        assert isinstance(node.is_foundation, bool)
        for prereq in node.prerequisites:
            validate_node(prereq)

    validate_node(tree)
```

---

## Moving to a Real Agent Framework

When you're ready to use a proper agent framework, here's what to do:

### Option 1: Anthropic's Extended Features

```python
# Using tool calling (available in Anthropic API)

from anthropic import Anthropic

client = Anthropic()

# Define tools
tools = [
    {
        "name": "search_curriculum",
        "description": "Search university curricula for prerequisite information",
        "input_schema": {
            "type": "object",
            "properties": {
                "concept": {"type": "string"},
                "university": {"type": "string"}
            },
            "required": ["concept"]
        }
    }
]

# Agent can now request tool use
response = client.messages.create(
    model="claude-sonnet-4.5-20251022",
    max_tokens=1024,
    tools=tools,
    messages=[{
        "role": "user",
        "content": "Find prerequisites for cosmology"
    }]
)

# Check if Claude wants to use a tool
if response.stop_reason == "tool_use":
    tool_use = response.content[-1]
    print(f"Claude wants to use: {tool_use.name}")
    print(f"With arguments: {tool_use.input}")
```

### Option 2: LangChain with Claude

```python
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatAnthropic

# Define tools
tools = [
    Tool(
        name="WebSearch",
        func=lambda q: search_web(q),
        description="Search the web for information"
    ),
    Tool(
        name="ReadFile",
        func=lambda path: read_file(path),
        description="Read content from a file"
    )
]

# Create agent
llm = ChatAnthropic(model="claude-sonnet-4.5-20251022")
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True  # ← Shows reasoning steps
)

# Run agent
result = agent.run("Find prerequisites for cosmology and validate against MIT's curriculum")

# LangChain will automatically show:
# - Thought: I need to search for MIT's cosmology course
# - Action: WebSearch
# - Action Input: "MIT cosmology prerequisites"
# - Observation: [search results]
# - Thought: Now I should compare...
```

### Option 3: Build Your Own Agent Loop

```python
class SimpleAgent:
    """Minimal agent with tool calling"""

    def __init__(self, tools, max_iterations=5):
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations

    def run(self, task):
        """Execute task with tool calling"""
        conversation = []

        for iteration in range(self.max_iterations):
            # Get Claude's next action
            response = client.messages.create(
                model="claude-sonnet-4.5-20251022",
                messages=conversation + [{
                    "role": "user",
                    "content": task if iteration == 0 else "Continue"
                }],
                tools=[tool.to_dict() for tool in self.tools.values()]
            )

            # Check if Claude wants to use a tool
            if response.stop_reason == "tool_use":
                tool_use = response.content[-1]
                tool_name = tool_use.name
                tool_input = tool_use.input

                print(f"[AGENT] Using tool: {tool_name}")
                print(f"[AGENT] Input: {tool_input}")

                # Execute tool
                tool_result = self.tools[tool_name].execute(tool_input)

                print(f"[AGENT] Result: {tool_result}")

                # Add to conversation
                conversation.extend([
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": tool_result
                    }]}
                ])
            else:
                # Task complete
                return response.content[0].text

        return "Max iterations reached"

# Usage
agent = SimpleAgent(tools=[WebSearchTool(), FileReadTool()])
result = agent.run("Find prerequisites for cosmology")
```

---

## Debugging Checklist

When something goes wrong with your agents:

1. **Print the prompts** - Are you asking Claude the right question?
2. **Check API responses** - Is Claude answering in the expected format?
3. **Verify JSON parsing** - Are you correctly extracting structured data?
4. **Monitor API calls** - Are you making too many calls? Cache hits?
5. **Validate assumptions** - Is the concept actually foundational?
6. **Test edge cases** - What happens with unusual inputs?
7. **Check token limits** - Are prompts/responses being truncated?
8. **Review error logs** - What exceptions are being caught?

---

## Next Steps

1. **Add logging** to your existing agents (start with Method 1 above)
2. **Create unit tests** for ConceptAnalyzer and PrerequisiteExplorer
3. **Build a metrics dashboard** to track agent performance
4. **Experiment with tool calling** using Anthropic's API features
5. **Document agent behavior** - what prompts work best?

---

## Resources

- **Anthropic Tool Use Guide**: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- **Agent Building Best Practices**: https://docs.anthropic.com/en/docs/agents
- **LangChain Claude Integration**: https://python.langchain.com/docs/integrations/chat/anthropic
- **Model Context Protocol (MCP)**: https://modelcontextprotocol.io/

---

**Last Updated**: 2025-10-04
**Author**: Agent Inspection Guide for Math-To-Manim
