"""
Math-To-Manim Web Interface
Powered by Claude Sonnet 4.5 and the Claude Agent SDK
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import gradio as gr
from anthropic import Anthropic

# Local agent imports (support both package and script execution)
try:  # pragma: no cover - import shim
    from .agents import VideoReviewAgent, VideoReviewResult  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - fallback when running as `python src/app_claude.py`
    import sys

    SRC_DIR = Path(__file__).resolve().parent
    if str(SRC_DIR) not in sys.path:
        sys.path.append(str(SRC_DIR))
    from agents import VideoReviewAgent, VideoReviewResult  # type: ignore[import]

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client for Claude Sonnet 4.5
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Model configuration
CLAUDE_MODEL = "claude-sonnet-4.5-20251022"  # Latest Sonnet 4.5

# Optional video review agent (used once we have generated output)
video_review_agent: Optional[VideoReviewAgent] = None

# Verify API key is present
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please check your .env file.")


def format_latex(text):
    """Format inline LaTeX expressions for proper rendering in Gradio."""
    # Replace single dollar signs with double for better display
    lines = text.split('\n')
    formatted_lines = []

    for line in lines:
        # Skip lines that already have double dollars
        if '$$' in line:
            formatted_lines.append(line)
            continue

        # Format single dollar expressions
        in_math = False
        new_line = ''
        for i, char in enumerate(line):
            if char == '$' and (i == 0 or line[i-1] != '\\'):
                in_math = not in_math
                new_line += '$$' if in_math else '$$'
            else:
                new_line += char
        formatted_lines.append(new_line)

    return '\n'.join(formatted_lines)


def process_simple_prompt(simple_prompt):
    """
    Process a simple prompt using Claude to create a detailed Manim prompt.

    This will eventually use the reverse knowledge tree system,
    but for now provides a template-based expansion.
    """
    system_prompt = """You are an expert at creating detailed, LaTeX-rich prompts for Manim animations.

Transform the user's simple description into a comprehensive, 2000+ token prompt that:
1. Specifies every visual element (colors, positions, sizes)
2. Uses proper LaTeX formatting for all equations
3. Provides sequential instructions ("Begin by...", "Next...", "Then...")
4. Maintains visual continuity between scenes
5. Includes timing information
6. Specifies camera movements
7. Color-codes mathematical objects consistently

The output should be detailed enough for an AI to generate working Manim Community Edition code."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            temperature=0.7,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"Create a detailed Manim animation prompt for: {simple_prompt}"
            }]
        )

        return format_latex(response.content[0].text)
    except Exception as e:
        return f"Error: {str(e)}"


def run_video_review(video_path: str) -> str:
    """Invoke the prototype VideoReview agent on a rendered video."""

    global video_review_agent  # noqa: PLW0603

    if video_review_agent is None:
        video_review_agent = VideoReviewAgent()

    try:
        result: VideoReviewResult = video_review_agent.review(Path(video_path))
        return (
            "Video review completed.\n\n"
            f"Frames directory: {result.frames_dir}\n"
            f"Web player: {result.web_player_path}\n"
            f"Metadata: {result.metadata}\n"
        )
    except Exception as exc:  # noqa: BLE001
        return f"Video review failed: {exc}"


def chat_with_claude(message, history):
    """
    Chat with Claude Sonnet 4.5 for generating Manim code or discussing concepts.
    """
    # Convert history to the format expected by the API
    messages = []
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    system_prompt = """You are an expert Manim animator and mathematics educator.

You help users:
1. Understand mathematical concepts
2. Generate Manim Community Edition code for animations
3. Create detailed animation prompts
4. Debug Manim code issues
5. Suggest visual representations for mathematical ideas

When generating Manim code:
- Use proper imports: from manim import *
- Define Scene classes with construct() method
- Use LaTeX for mathematical expressions (raw strings)
- Provide comments explaining the animation logic
- Use appropriate colors and positioning
- Include timing information (wait, play durations)

Always format LaTeX with proper escaping and use MathTex() for equations."""

    # Call the Claude API
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            temperature=0.7,
            system=system_prompt,
            messages=messages
        )

        answer = format_latex(response.content[0].text)
        return answer
    except Exception as e:
        return f"Error: {str(e)}"


# Create Gradio interface with tabs for different modes
with gr.Blocks(theme="soft", title="Math-To-Manim - Claude Sonnet 4.5") as iface:
    gr.Markdown("# Math-To-Manim Generator")
    gr.Markdown("*Powered by Claude Sonnet 4.5 and the Claude Agent SDK*")

    with gr.Tab("Standard Mode"):
        gr.Markdown("""
        ### Chat with Claude Sonnet 4.5

        Get help with:
        - Understanding mathematical concepts
        - Generating Manim code
        - Creating animation ideas
        - Debugging issues

        Claude has been optimized for mathematical visualization and Manim code generation.
        """)

        chat_interface = gr.ChatInterface(
            chat_with_claude,
            examples=[
                "Generate Manim code to visualize the Pythagorean theorem",
                "Explain how to animate a Fourier series in Manim",
                "Create a 3D visualization of a rotating torus",
                "Show me how to display mathematical equations with proper LaTeX"
            ],
            title="",
            description=""
        )

    with gr.Tab("Prompt Expander"):
        gr.Markdown("""
        ### Transform Simple Ideas into Detailed Prompts

        This mode takes your simple description and expands it into a comprehensive,
        LaTeX-rich prompt suitable for generating high-quality Manim animations.

        **Future**: This will use the reverse knowledge tree system to build animations
        from foundational concepts up to advanced topics.
        """)

        simple_input = gr.Textbox(
            label="Simple Description",
            placeholder="Example: Show the Pythagorean theorem with a visual proof",
            lines=3
        )
        simple_submit = gr.Button("Expand Prompt", variant="primary")
        detailed_output = gr.Textbox(
            label="Detailed Manim Prompt",
            lines=15
        )

        simple_submit.click(
            fn=process_simple_prompt,
            inputs=simple_input,
            outputs=detailed_output
        )

        gr.Examples(
            examples=[
                "Visualize quantum entanglement",
                "Explain the Fourier transform with animations",
                "Show how calculus derivatives work geometrically",
                "Animate the concept of eigenvectors and eigenvalues"
            ],
            inputs=simple_input
        )

    with gr.Tab("Knowledge Tree (Coming Soon)"):
        gr.Markdown("""
        ### Reverse Knowledge Tree System

        This revolutionary approach will:

        1. **Analyze** your question ("Explain cosmology")
        2. **Recursively decompose** the concept by asking:
           - "To understand cosmology, what must I know first?"
           - "To understand general relativity, what must I know first?"
           - Continue until reaching foundation concepts (high school level)
        3. **Build from foundations** up to the target concept
        4. **Generate animations** that teach from the ground up

        **Status**: Architecture designed, implementation in progress

        **Powered by**: Claude Sonnet 4.5's superior reasoning capabilities

        See `prerequisite_explorer_claude.py` for the working prototype.
        """)

        gr.Image(
            value=None,
            label="Knowledge Tree Visualization (Coming Soon)",
            interactive=False
        )

    with gr.Tab("Video Review (Prototype)"):
        gr.Markdown("""
        ### Automate Post-Render QA (Prototype)

        Once your animation is rendered to MP4, you can point the VideoReview agent at it.

        The agent will:
        - extract frames into `media/review_frames/<scene>/`
        - generate an HTML5 review player
        - collect video metadata from ffprobe

        This tab currently calls the agent directly; soon it will run automatically at the end of the pipeline.
        """)

        review_input = gr.Textbox(
            label="Path to rendered MP4",
            placeholder="media/videos/bhaskara_epic_manim/480p15/BhaskaraEpic.mp4",
            lines=1,
        )
        review_button = gr.Button("Run Video Review", variant="primary")
        review_output = gr.Textbox(label="Agent Output", lines=6)

        review_button.click(fn=run_video_review, inputs=review_input, outputs=review_output)

    with gr.Tab("About"):
        gr.Markdown("""
        ## Math-To-Manim

        Transform mathematical concepts into beautiful animations using AI-powered generation.

        ### Technology Stack

        - **AI Model**: Claude Sonnet 4.5 (latest, Oct 2025)
        - **Agent Framework**: Claude Agent SDK
        - **Animation**: Manim Community Edition v0.19.0
        - **Interface**: Gradio

        ### Key Innovation: Reverse Knowledge Tree

        Unlike traditional AI systems that require training data, our approach uses
        **recursive conceptual decomposition**:

        1. Ask "What must I understand BEFORE X?"
        2. Build a complete knowledge tree from foundations
        3. Generate animations that teach progressively
        4. No training data required - pure reasoning!

        ### Resources

        - [GitHub Repository](https://github.com/HarleyCoops/Math-To-Manim)
        - [Documentation](docs/README.md)
        - [Roadmap](ROADMAP.md)
        - [Reverse Knowledge Tree Spec](REVERSE_KNOWLEDGE_TREE.md)

        ### System Requirements

        - Python 3.10+
        - FFmpeg (for video rendering)
        - Node.js (for Claude Agent SDK)
        - LaTeX distribution (for study notes)

        ### Environment Variables Required

        ```bash
        ANTHROPIC_API_KEY=your_claude_api_key_here
        ```

        Get your API key from: [https://console.anthropic.com/](https://console.anthropic.com/)
        """)


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║             Math-To-Manim Web Interface                          ║
║                                                                   ║
║  Powered by: Claude Sonnet 4.5 (claude-sonnet-4.5-20251022)     ║
║  Framework: Claude Agent SDK                                     ║
║                                                                   ║
║  Starting Gradio interface...                                    ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    iface.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860
    )
