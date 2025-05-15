# Smolagents Implementation for Math-To-Manim

This document outlines the implementation plan for integrating the Hugging Face smolagents framework with Math-To-Manim to create a more accessible and powerful mathematical animation generation system.

## Overview

The smolagents integration will transform simple, natural language descriptions into the detailed, LaTeX-rich prompts required by the LLM to generate high-quality Manim code. This will make the system more accessible to users who may not have the expertise to write the detailed prompts currently required.

## Implementation Steps

### 1. Agent Definition

```python
from smolagents import Agent, Tool

class MathToManimAgent(Agent):
    """Agent for transforming simple math descriptions into detailed Manim prompts."""
    
    def __init__(self, model_name="deepseek-ai/DeepSeek-R1-Zero"):
        super().__init__(model_name=model_name)
        self.register_tools([
            self.enhance_prompt,
            self.validate_latex,
            self.validate_manim_code
        ])
    
    @Tool
    def enhance_prompt(self, simple_prompt: str) -> str:
        """
        Transform a simple mathematical description into a detailed, LaTeX-rich prompt.
        
        Args:
            simple_prompt: A simple description of the desired animation
            
        Returns:
            A detailed, LaTeX-rich prompt suitable for generating Manim code
        """
        # Implementation will use few-shot examples and specific instructions
        # to transform the simple prompt into a detailed one
        pass
    
    @Tool
    def validate_latex(self, latex_content: str) -> dict:
        """
        Validate LaTeX syntax in the prompt.
        
        Args:
            latex_content: LaTeX content to validate
            
        Returns:
            Dictionary with validation results and suggestions
        """
        # Implementation will check for common LaTeX errors and provide suggestions
        pass
    
    @Tool
    def validate_manim_code(self, manim_code: str) -> dict:
        """
        Validate generated Manim code for common errors.
        
        Args:
            manim_code: Generated Manim code
            
        Returns:
            Dictionary with validation results and suggestions
        """
        # Implementation will check for common Manim errors and provide suggestions
        pass
```

### 2. Training Data Collection

To train the smolagent effectively, we need to collect pairs of simple prompts and their corresponding detailed, LaTeX-rich prompts. This data will come from:

1. **Existing Examples**: Extract prompt-code pairs from the repository
2. **Synthetic Examples**: Generate additional examples by simplifying existing detailed prompts
3. **User Contributions**: Collect contributions from the community

Example data format:
```json
[
  {
    "simple_prompt": "Show the Pythagorean theorem with a visual proof",
    "detailed_prompt": "Begin with a square with side length a+b. Inside this square, construct a right triangle with sides a and b, and hypotenuse c. Then, rearrange the four identical right triangles to show that the area of the square of the hypotenuse equals the sum of the areas of the squares on the other two sides. Use color coding: the right triangle in blue, the square of side a in red, the square of side b in green, and the square of side c in purple. Add labels for each side and each area. Include the equation a² + b² = c² that appears and pulses when the proof is complete."
  },
  {
    "simple_prompt": "Visualize a quantum field",
    "detailed_prompt": "Create a 3D visualization of a quantum field. Start with a 3D grid representing space. Add oscillating waves in different colors to represent different field values. Show particles as excitations in the field - bright spots where the field value is high. Demonstrate how particles interact by showing ripples propagating through the field when particles come close to each other. Include labels and a legend explaining the components. Use equations like \\hat{\\phi}(x) = \\int \\frac{d^3p}{(2\\pi)^3} \\frac{1}{\\sqrt{2E_p}} (a_p e^{-ip \\cdot x} + a_p^\\dagger e^{ip \\cdot x}) to describe the quantum field."
  }
]
```

### 3. Training Process

The training process will involve:

1. **Fine-tuning**: Fine-tune the base model on the collected prompt pairs
2. **Reinforcement Learning**: Use reinforcement learning to improve the agent based on success/failure of generated animations
3. **Evaluation**: Regularly evaluate the agent's performance on a test set of prompts

Training script outline:
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained("deepseek-ai/DeepSeek-R1-Zero")
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Zero")

# Prepare dataset
def prepare_dataset(data):
    inputs = []
    for item in data:
        # Format as instruction
        text = f"Convert this simple math animation description into a detailed, LaTeX-rich prompt:\n\nSimple: {item['simple_prompt']}\n\nDetailed:"
        inputs.append(text)
    
    labels = [item["detailed_prompt"] for item in data]
    return {"input": inputs, "output": labels}

# Load and prepare data
with open("prompt_pairs.json", "r") as f:
    data = json.load(f)

prepared_data = prepare_dataset(data)
dataset = Dataset.from_dict(prepared_data)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=1000,
    save_total_limit=2,
    logging_dir="./logs",
)

# Train model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

trainer.train()
```

### 4. Integration with Math-To-Manim

The integration will involve:

1. **API Endpoint**: Create an API endpoint for the smolagent
2. **User Interface**: Update the UI to support simple prompts
3. **Feedback Collection**: Add mechanisms to collect user feedback

Integration code outline:
```python
import os
from dotenv import load_dotenv
import gradio as gr
from openai import OpenAI
from smolagents import MathToManimAgent

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Initialize smolagent
agent = MathToManimAgent()

def process_simple_prompt(simple_prompt):
    """Process a simple prompt using the smolagent."""
    detailed_prompt = agent.enhance_prompt(simple_prompt)
    return detailed_prompt

def generate_manim_code(prompt, use_smolagent=False):
    """Generate Manim code from a prompt."""
    if use_smolagent:
        prompt = process_simple_prompt(prompt)
    
    # Call the DeepSeek API
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content, prompt

# Create Gradio interface
with gr.Blocks() as iface:
    gr.Markdown("# Math-To-Manim Generator")
    
    with gr.Tab("Simple Mode (with Smolagent)"):
        simple_input = gr.Textbox(label="Simple Description", lines=5)
        simple_submit = gr.Button("Generate")
        detailed_output = gr.Textbox(label="Detailed Prompt (Generated)", lines=10)
        code_output_simple = gr.Code(label="Generated Manim Code", language="python")
        
        simple_submit.click(
            fn=lambda x: generate_manim_code(x, use_smolagent=True),
            inputs=simple_input,
            outputs=[code_output_simple, detailed_output]
        )
    
    with gr.Tab("Advanced Mode (Direct Prompt)"):
        advanced_input = gr.Textbox(label="Detailed Prompt", lines=10)
        advanced_submit = gr.Button("Generate")
        code_output_advanced = gr.Code(label="Generated Manim Code", language="python")
        
        advanced_submit.click(
            fn=lambda x: generate_manim_code(x, use_smolagent=False)[0],
            inputs=advanced_input,
            outputs=code_output_advanced
        )

if __name__ == "__main__":
    iface.launch()
```

### 5. Feedback Loop

To continuously improve the smolagent, we'll implement a feedback loop:

1. **Success/Failure Tracking**: Track whether the generated Manim code successfully renders
2. **User Ratings**: Allow users to rate the quality of the prompt transformation
3. **Error Analysis**: Analyze common failure patterns

Feedback collection code outline:
```python
def collect_feedback(simple_prompt, detailed_prompt, manim_code, success, rating=None):
    """Collect feedback on the smolagent's performance."""
    feedback_data = {
        "simple_prompt": simple_prompt,
        "detailed_prompt": detailed_prompt,
        "manim_code": manim_code,
        "success": success,
        "rating": rating,
        "timestamp": datetime.now().isoformat()
    }
    
    # Save feedback to database or file
    with open("feedback_log.jsonl", "a") as f:
        f.write(json.dumps(feedback_data) + "\n")
    
    # If we have enough new feedback, trigger retraining
    check_and_trigger_retraining()
```

## Deployment Plan

1. **Alpha Release (Month 1)**
   - Basic smolagent implementation
   - Limited prompt types
   - Internal testing

2. **Beta Release (Month 2)**
   - Expanded prompt capabilities
   - Community testing
   - Feedback collection

3. **Full Release (Month 3)**
   - Complete integration
   - Documentation
   - Performance optimization

## Evaluation Metrics

We'll evaluate the smolagent using the following metrics:

1. **Prompt Quality**: How well the detailed prompt captures the intent of the simple prompt
2. **Success Rate**: Percentage of generated Manim code that successfully renders
3. **User Satisfaction**: Ratings from users on the quality of the transformations
4. **Efficiency**: Time taken to transform prompts and generate code

## Resources Required

1. **Compute Resources**
   - Training: GPU with at least 16GB VRAM
   - Inference: CPU for smolagent, GPU for LLM

2. **Storage**
   - Training data: ~1GB
   - Model checkpoints: ~10GB

3. **Development Time**
   - Initial implementation: 2 weeks
   - Training and optimization: 2 weeks
   - Integration: 1 week
   - Testing and refinement: 3 weeks

## Conclusion

The smolagents integration will significantly enhance the Math-To-Manim system by making it more accessible to users without expertise in writing detailed, LaTeX-rich prompts. This will expand the potential user base and enable more people to create high-quality mathematical animations.

