# Google Gemini 3 Agent Pipeline

This pipeline leverages the **Google Agent Development Kit (ADK)** and the reasoning capabilities of **Gemini 3** to generate Manim animations from natural language prompts.

## Architecture

The system uses a **Six-Agent Swarm** architecture:

1.  **ConceptAnalyzer**: Deconstructs user prompts into core mathematical concepts, target audience, and difficulty levels.
2.  **PrerequisiteExplorer**: Builds a directed acyclic graph (DAG) of knowledge dependencies ("What must be understood before X?").
3.  **MathematicalEnricher**: Populates the knowledge tree with precise LaTeX definitions, equations, and theorems.
4.  **VisualDesigner**: Translates abstract concepts into concrete visual metaphors (shapes, colors, camera movements).
5.  **NarrativeComposer**: Weaves the visual elements into a cohesive educational narrative, generating a verbose 2000+ token prompt.
6.  **CodeGenerator**: Converts the verbose narrative into executable Python code using the Manim library.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    Ensure you have `manim` installed (requires FFmpeg and LaTeX).

2.  **API Key**:
    Get a Google Cloud API Key with access to Gemini models.
    ```bash
    export GOOGLE_API_KEY="your_api_key_here"
    # Or add to .env
    echo "GOOGLE_API_KEY=your_key_here" >> .env
    ```

## Usage

Run the pipeline with a simple text prompt:

```bash
python Gemini3/run_pipeline.py "Explain the concept of a Fourier Transform"
```

The pipeline will:
1.  Display agent thoughts and progress in the terminal.
2.  Generate a `output_scene.py` file (or similar, depending on configuration).
3.  Provide the command to render the animation.

## Comparison with Other Pipelines

| Feature | Gemini 3 (Google ADK) | Claude Sonnet 4.5 (Anthropic SDK) | Kimi K2 (Thinking Model) |
| :--- | :--- | :--- | :--- |
| **Framework** | Google ADK | Anthropic Agent SDK | OpenAI-compatible API |
| **Strengths** | Complex Reasoning, Topology | Recursive Logic, Code Generation | Chain-of-Thought, structured tools |
| **Best For** | Physics, Advanced Math | General Purpose, Reliable Code | LaTeX-heavy explanations |

## Troubleshooting

-   **LaTeX Errors**: If the animation fails to render due to LaTeX errors, usually the error message from Manim is sufficient to manually fix the `Tex` or `MathTex` string in the generated Python file.
-   **Authentication**: Ensure `GOOGLE_API_KEY` is set correctly.
