# Math-To-Manim Architecture

This document outlines the architecture of the Math-To-Manim system, including the current implementation and the planned smolagents integration.

## Current Architecture

The current Math-To-Manim system follows a simple workflow:

```
User Prompt (LaTeX-rich) -> DeepSeek/Gemini/Grok3 -> Manim Code -> Rendering -> Animation
```

### Components

1. **User Interface (app.py)**
   - Gradio-based web interface
   - Allows users to input detailed prompts
   - Communicates with the DeepSeek API

2. **AI Model Integration**
   - DeepSeek R1-Zero (primary model)
   - Google Gemini (supplementary model)
   - Grok3 (supplementary model)
   - Models are accessed via their respective APIs

3. **Code Generation**
   - AI models generate Manim Python code based on the prompt
   - The code is saved as a Python file

4. **Rendering Engine**
   - Manim Community Edition
   - Renders the generated Python code into animations
   - Requires FFmpeg for video processing

5. **Documentation Generation**
   - AI models can generate LaTeX study notes
   - Notes explain the mathematical concepts in the animation

## Planned Smolagents Integration

The planned smolagents integration will enhance the system with a more sophisticated workflow:

```
User Prompt (Simple) -> Smolagent -> Detailed LaTeX-rich Prompt -> DeepSeek/Gemini/Grok3 -> Manim Code -> Rendering -> Animation
```

### New Components

1. **Smolagent**
   - Hugging Face smolagents framework
   - Trained on a dataset of simple-to-detailed prompt pairs
   - Transforms basic user descriptions into the detailed prompts required by the LLM

2. **Enhanced User Interface**
   - Simplified input requirements for users
   - Interactive refinement of prompts
   - Preview of the detailed prompt before submission

3. **Feedback Loop**
   - Captures successful and failed generations
   - Uses this data to improve the smolagent's prompt transformation

### Smolagent Implementation

The smolagent will be implemented using the Hugging Face smolagents framework, which provides:

1. **Agent Definition**
   - Custom agent class inheriting from the base smolagent
   - Specialized for mathematical visualization prompts

2. **Tools**
   - Prompt enhancement tool
   - LaTeX validation tool
   - Manim code validation tool

3. **Memory**
   - Stores successful prompt transformations
   - Remembers user preferences and common patterns

4. **Training**
   - Fine-tuned on a dataset of simple-to-detailed prompt pairs
   - Reinforcement learning from user feedback

## Integration Points

The smolagent will be integrated into the system at the following points:

1. **User Interface**
   - New input field for simple prompts
   - Option to bypass the smolagent for advanced users

2. **API Layer**
   - New endpoint for smolagent-enhanced prompts
   - Backward compatibility with direct prompts

3. **Feedback Collection**
   - Success/failure tracking of generated animations
   - User ratings of prompt transformations

## Data Flow

1. User submits a simple description of the desired animation
2. Smolagent transforms this into a detailed, LaTeX-rich prompt
3. User reviews and optionally edits the detailed prompt
4. Detailed prompt is sent to the AI model (DeepSeek/Gemini/Grok3)
5. AI model generates Manim code
6. Manim renders the code into an animation
7. Success/failure and user feedback are collected for smolagent improvement

## Technical Requirements

1. **Smolagents Framework**
   - Install via: `pip install smolagents`
   - Requires Python 3.8+

2. **Training Data**
   - Dataset of simple-to-detailed prompt pairs
   - Existing successful prompts from the repository

3. **Compute Resources**
   - Training: GPU recommended
   - Inference: CPU sufficient for smolagent, GPU recommended for AI models

## Implementation Plan

1. **Phase 1: Data Collection**
   - Gather successful prompt pairs
   - Create synthetic examples

2. **Phase 2: Smolagent Development**
   - Define agent architecture
   - Implement tools
   - Train initial model

3. **Phase 3: Integration**
   - Update user interface
   - Add API endpoints
   - Implement feedback collection

4. **Phase 4: Testing & Refinement**
   - User testing
   - Performance optimization
   - Iterative improvement

## Future Extensions

1. **Multi-modal Input**
   - Accept sketches or images as input
   - Extract mathematical concepts from handwritten notes

2. **Interactive Editing**
   - Real-time preview of animation changes
   - Interactive parameter adjustment

3. **Collaborative Creation**
   - Multiple users working on the same animation
   - Version control for animations

4. **Educational Platform**
   - Integration with learning management systems
   - Curriculum-aligned animation generation

