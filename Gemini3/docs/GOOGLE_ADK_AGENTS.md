# Google ADK Agents with Gemini 3 Pro

This document outlines the architecture and implementation details for the Agent Development Kit (ADK) pipeline powered by Google's Gemini 3 Pro model.

## 1. Core Technologies

### 1.1 Google ADK (Agent Development Kit)
The `google-adk` Python library is a code-first toolkit for building, evaluating, and deploying AI agents.
- **Key Components:**
    - `Agent` / `LlmAgent`: The fundamental building block representing an autonomous entity.
    - `Tool`: Functions or capabilities exposed to the agent (e.g., web search, code execution).
    - `Model`: The underlying LLM (in our case, Gemini 3 Pro).
    - `Orchestration`: Mechanisms for agents to communicate and hand off tasks.

### 1.2 Gemini 3 Pro
Gemini 3 Pro is Google's most powerful agentic model, featuring:
- **Thinking Mode:** Capable of reasoning through thoughts before responding.
- **Multimodal Understanding:** Best-in-class handling of text, images, and code.
- **1M Token Context:** Allows for massive context retention across the agent pipeline.
- **Model Name:** `gemini-3.0-pro-preview` (or `gemini-experiment` as fallback).

## 2. Architecture: The Math-To-Manim Pipeline

The pipeline consists of specialized agents working in a strictly defined sequence to transform a user prompt into a mathematical animation.

### 2.1 Agent Roles

1.  **ConceptAnalyzer**
    *   **Input:** User prompt (e.g., "Explain Quantum Gravity").
    *   **Role:** Deconstructs the request, identifies the core mathematical domains, and determines the target audience and difficulty level.
    *   **Output:** A structured analysis object (JSON).

2.  **PrerequisiteExplorer**
    *   **Input:** Concept analysis.
    *   **Role:** Recursively asks "What must be understood before X?" to build a dependency tree of concepts.
    *   **Tool:** Recursive graph builder.
    *   **Output:** A Directed Acyclic Graph (DAG) of concepts.

3.  **MathematicalEnricher**
    *   **Input:** Concept tree.
    *   **Role:** For each node in the tree, adds precise LaTeX definitions, equations, and theorems. Ensures mathematical rigor.
    *   **Output:** Enriched Knowledge Tree (JSON).

4.  **VisualDesigner**
    *   **Input:** Enriched Knowledge Tree.
    *   **Role:** Maps mathematical concepts to visual metaphors. Describes scenes, camera movements, colors (using Manim best practices), and transitions.
    *   **Output:** Visual Storyboard.

5.  **NarrativeComposer**
    *   **Input:** Visual Storyboard + Enriched Tree.
    *   **Role:** Weaves a narrative thread through the concepts. Generates the final verbose prompt that acts as the specification for the code generator.
    *   **Output:** A 2000+ token verbose prompt (The "Golden Prompt").

6.  **CodeGenerator**
    *   **Input:** Verbose prompt.
    *   **Role:** Translates the detailed specification into executable Manim Python code.
    *   **Tool:** Python Code Execution / File Writing.
    *   **Output:** `.py` file containing the animation script.

## 3. Implementation Details

### 3.1 Directory Structure (`Gemini3/`)
```
Gemini3/
├── src/
│   ├── core.py       # Configuration, Logging, Base Classes
│   ├── agents.py     # Agent definitions
│   └── pipeline.py   # Orchestration logic
├── run_pipeline.py   # CLI Entry point
└── docs/             # Documentation
```

### 3.2 Logging & Visibility
- We use the `rich` library to provide a real-time TUI.
- All agent "thoughts" (reasoning traces) and tool outputs are streamed to the console.
- Handoffs between agents are clearly visualized.

### 3.3 Model Configuration
All agents are initialized with:
```python
model_config = {
    "model_name": "gemini-3.0-pro-preview",
    "temperature": 0.7,  # Adjustable per agent
    "safety_settings": ...
}
```

## 4. Future Extensibility
- **Meta-Analysis:** The pipeline structure allows for a "Supervisor" agent to inspect the logs (captured by `core.py`) and generate a report on agent collaboration efficiency.
- **Interoperability:** Trace data can be exported to OpenTelemetry or simple JSON logs for external analysis.
