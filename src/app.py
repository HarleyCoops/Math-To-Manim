import os
from dotenv import load_dotenv
import gradio as gr
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with DeepSeek base URL
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Initialize smolagent (commented out until smolagents is available)
# smolagent = MathToManimAgent()

# Verify API key is present
if not os.getenv("DEEPSEEK_API_KEY"):
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set. Please check your .env file.")

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
    Process a simple prompt using the smolagent to create a detailed prompt.
    This function is a placeholder until smolagents is available.
    """
    # In a real implementation, this would use the smolagent
    # For now, we'll return a template-based detailed prompt
    return f"""Begin by setting up a scene with a title "{simple_prompt}" at the top.
    
Create a clear visual representation of the mathematical concept with appropriate colors and labels.

Use LaTeX for all mathematical expressions, ensuring they are properly formatted with \\begin{{align}} and \\end{{align}} for equations.

Include step-by-step animations that build up the concept gradually, with each step clearly labeled.

Add textual explanations that appear alongside the visuals to explain key concepts.

Ensure all symbols are defined when they first appear, and use consistent notation throughout.

End with a summary that reinforces the key insights from the animation."""

def chat_with_deepseek(message, history, use_smolagent=False):
    # Process with smolagent if requested
    if use_smolagent:
        message = process_simple_prompt(message)
    
    # Convert history to the format expected by the API
    messages = []
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})
    
    # Call the DeepSeek API
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",  # Latest: deepseek-r1 or deepseek-chat for stable production
            messages=messages
        )
        
        # Get both reasoning and final content
        reasoning = format_latex(response.choices[0].message.reasoning_content)
        answer = format_latex(response.choices[0].message.content)
        
        # Return both, separated by a clear delimiter
        return f"🤔 Reasoning:\n{reasoning}\n\n[NOTE] Answer:\n{answer}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface with tabs for different modes
with gr.Blocks(theme="soft") as iface:
    gr.Markdown("# Math-To-Manim Generator")
    
    with gr.Tab("Standard Mode"):
        chat_interface = gr.ChatInterface(
            chat_with_deepseek,
            title="DeepSeek Reasoning Chat",
            description="Chat with DeepSeek's Reasoning model. The model will show its reasoning process before providing the final answer. Supports LaTeX math expressions using $ or $$.",
        )
    
    with gr.Tab("Smolagent Mode (Coming Soon)"):
        gr.Markdown("""
        # Smolagent Mode
        
        This mode will allow you to input simple descriptions of mathematical animations and have them automatically transformed into detailed, LaTeX-rich prompts.
        
        ## Example:
        
        **Simple Prompt**: "Show the Pythagorean theorem with a visual proof"
        
        **Transformed into**: A detailed prompt with specific instructions for colors, animations, equations, and explanations.
        
        ## Status:
        
        This feature is currently in development and will be available soon. Stay tuned!
        """)
        
        simple_input = gr.Textbox(
            label="Simple Description",
            placeholder="Describe the mathematical animation you want to create...",
            lines=5
        )
        simple_submit = gr.Button("Transform Prompt (Preview)")
        detailed_output = gr.Textbox(
            label="Detailed Prompt (Preview)",
            lines=10
        )
        
        # Connect the simple input to the process_simple_prompt function
        simple_submit.click(
            fn=process_simple_prompt,
            inputs=simple_input,
            outputs=detailed_output
        )

if __name__ == "__main__":
    iface.launch()
