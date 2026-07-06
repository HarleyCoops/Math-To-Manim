"""Optional Gradio interface."""

from __future__ import annotations

from math_to_manim.config import RuntimeConfig
from math_to_manim.pipeline.runner import AnimationPipeline


def create_demo():
    try:
        import gradio as gr
    except ImportError as exc:
        raise RuntimeError("Install the web extra to use Gradio: pip install -e .[web]") from exc

    pipeline = AnimationPipeline(RuntimeConfig.from_env())

    def generate(prompt: str, style: str, render: bool):
        package = pipeline.generate(prompt=prompt, style=style, render=render)
        return package.to_public_dict()

    with gr.Blocks(title="Math-To-Manim Codex") as demo:
        prompt = gr.Textbox(label="Prompt", value="Explain why derivatives are slopes")
        style = gr.Textbox(label="Style", value="cinematic")
        render = gr.Checkbox(label="Render with Manim", value=False)
        output = gr.JSON(label="Package")
        prompt.submit(generate, inputs=[prompt, style, render], outputs=output)
    return demo


if __name__ == "__main__":
    create_demo().launch()
