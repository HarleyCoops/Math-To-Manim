#!/usr/bin/env python3
"""SmolAgents Prompt Expander for Math-To-Manim."""

import sys
import argparse
import textwrap
import yaml
import importlib.resources

DEFAULT_SYSTEM_PROMPT = textwrap.dedent("""
You are an expert prompt engineer specializing in converting short, high-level user descriptions into extremely detailed, step-by-step animation directives for Manim.
Each instruction must use LaTeX for any mathematical expressions.
Your expanded prompt should guide the animation engine through scene setup, camera movements, text renderings, equation animations, and transitions.
Be explicit about durations, visual styles, colors, and scene composition.
Structure your output with clear sections and bullet points.
Do not include any code; only provide the LaTeX-based storyboard for the animation.
""").strip()

def main():

    parser = argparse.ArgumentParser(
        description="Expand basic prompts into detailed LaTeX prompts using SmolAgents"
    )
    parser.add_argument(
        "prompt",
        help="Basic user prompt to expand into a verbose LaTeX-based prompt",
    )
    parser.add_argument(
        "--model",
        default="deepseek-ai/PromptExpander",
        help="SmolAgents model name or path",
    )
    parser.add_argument(
        "--system-prompt",
        default=DEFAULT_SYSTEM_PROMPT,
        help="System instructions guiding the expansion template",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=2048,
        help="Maximum token length for the expanded prompt",
    )
    args = parser.parse_args()

    try:
        from smolagents import ToolCallingAgent
        from smolagents.models import InferenceClientModel
    except ImportError:
        print(
            "Error: smolagents package is not installed. "
            "Install with `pip install git+https://github.com/huggingface/smolagents.git@main`."
        )
        sys.exit(1)

    model = InferenceClientModel(model_id=args.model)
    default_templates = yaml.safe_load(
        importlib.resources.files("smolagents.prompts").joinpath("toolcalling_agent.yaml").read_text()
    )
    default_templates["system_prompt"] = args.system_prompt
    agent = ToolCallingAgent(tools=[], model=model, prompt_templates=default_templates)
    expanded = agent.run(args.prompt, max_steps=1)
    print(expanded)


if __name__ == "__main__":
    main()