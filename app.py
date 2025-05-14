import os
from dotenv import load_dotenv
import gradio as gr
from openai import OpenAI
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with DeepSeek base URL
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Initialize Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Verify API keys are present
if not os.getenv("DEEPSEEK_API_KEY"):
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set. Please check your .env file.")
if not os.getenv("GOOGLE_API_KEY"):
    print("Warning: GOOGLE_API_KEY environment variable is not set. Google AI features will be disabled.")

# Define available models
MODELS = {
    "deepseek-reasoner": {
        "provider": "deepseek",
        "name": "DeepSeek Reasoner",
        "description": "Specialized in mathematical reasoning and step-by-step problem solving."
    },
    "gemini-pro": {
        "provider": "google",
        "name": "Google Gemini Pro",
        "description": "Google's advanced model with strong mathematical and scientific capabilities."
    }
}

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

def chat_with_model(message, history, model_choice):
    """Chat with the selected AI model."""
    if model_choice not in MODELS:
        return "Error: Invalid model selection."
    
    model_info = MODELS[model_choice]
    
    # Convert history to the format expected by the API
    messages = []
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})
    
    # Call the appropriate API based on the selected model
    try:
        if model_info["provider"] == "deepseek":
            return chat_with_deepseek(messages, model_choice)
        elif model_info["provider"] == "google":
            return chat_with_google(messages, model_choice)
        else:
            return f"Error: Unsupported provider {model_info['provider']}"
    except Exception as e:
        return f"Error: {str(e)}"

def chat_with_deepseek(messages, model_name):
    """Call the DeepSeek API."""
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    
    # Get both reasoning and final content
    reasoning = format_latex(response.choices[0].message.reasoning_content)
    answer = format_latex(response.choices[0].message.content)
    
    # Return both, separated by a clear delimiter
    return f"🤔 Reasoning:\n{reasoning}\n\n📝 Answer:\n{answer}"

def chat_with_google(messages, model_name):
    """Call the Google Gemini API."""
    # Convert messages to Google's format
    google_messages = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        google_messages.append({"role": role, "parts": [{"text": msg["content"]}]})
    
    # Get the Gemini model
    model = genai.GenerativeModel(model_name)
    
    # Generate response
    response = model.generate_content(google_messages)
    
    # Format the response
    answer = format_latex(response.text)
    
    return f"📝 Answer:\n{answer}"

# Create Gradio interface with model selection
with gr.Blocks(theme="soft") as iface:
    gr.Markdown("# Math-To-Manim AI Assistant")
    gr.Markdown("Chat with AI models to generate mathematical animations and explanations. Supports LaTeX math expressions using $ or $$.")
    
    with gr.Row():
        model_dropdown = gr.Dropdown(
            choices=list(MODELS.keys()),
            value="deepseek-reasoner",
            label="Select AI Model",
            info="Choose which AI model to use for generating responses"
        )
    
    chatbot = gr.Chatbot(height=600)
    msg = gr.Textbox(
        placeholder="Enter your mathematical query or animation request...",
        container=False,
        scale=7
    )
    
    with gr.Row():
        submit = gr.Button("Submit")
        clear = gr.Button("Clear")
    
    def respond(message, chat_history, model_choice):
        bot_message = chat_with_model(message, chat_history, model_choice)
        chat_history.append((message, bot_message))
        return "", chat_history
    
    submit.click(respond, [msg, chatbot, model_dropdown], [msg, chatbot])
    msg.submit(respond, [msg, chatbot, model_dropdown], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    iface.launch()
