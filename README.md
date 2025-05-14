# Math-To-Manim

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=HarleyCoops/Math-To-Manim&type=Date)](https://star-history.com/#HarleyCoops/Math-To-Manim&Date)

## Project Overview 

This project uses DeepSeek AI, Google Gemini, and other models to generate mathematical animations using Manim with better prompts. It includes various examples of complex mathematical concepts visualized through animation. The intent here is to attempt to automatically chart concepts that far exceed most humans' capacity to visualize complex connections across math and physics in a one-shot animation.

**Technical Insight**:
- **LaTeX Matters**: Base prompt engineering technique yielding much better results for displaying formulas on screen.
- **Dual-Stream Output**: Simultaneous animation code + study notes generation. No model fine tuning necessary. Just pass any working python scene script back as a prompt and ask for "verbose explanations fully rendered as latext study notes.." and you will get working latex that renders into a PDF set at Overleaf.

**Key Features & Innovations**:
- **Cross-Model Synergy**: Leveraging multiple AI models (DeepSeek, Gemini, Grok3) allows for unique perspectives on mathematical visualization, often catching edge cases a single model might miss.
- **Educational Impact**: The generated animations serve as powerful teaching tools, breaking down complex mathematical concepts into visually digestible sequences.
- **Automated Documentation**: The system not only generates animations but also produces comprehensive LaTeX documentation, creating a complete learning package.
- **Adaptive Complexity**: Can handle everything from basic geometric proofs to advanced topics like quantum mechanics and optimal transport theory.
- **Interactive Development**: The project includes a feedback loop where successful animations can be used to improve prompt engineering for future generations.

**Real-World Applications**:
- **Academic Research**: Visualizing complex mathematical proofs and theories
- **Education**: Creating engaging materials for STEM courses
- **Scientific Communication**: Bridging the gap between abstract mathematics and visual understanding
- **Research Validation**: Providing visual verification of mathematical concepts and relationships

## Google AI Integration

This project now supports Google AI models (Gemini) alongside DeepSeek for generating mathematical animations. The integration provides:

1. **Model Selection**: Choose between DeepSeek Reasoner and Google Gemini Pro in the web interface
2. **Cloud Integration**: Optional Google Cloud services for hosting and rendering
3. **Enhanced Capabilities**: Leverage Google's advanced models for improved mathematical understanding

### Setting Up Google AI

1. Get a Google AI API key from [Google AI Studio](https://makersuite.google.com/)
2. Add your API key to the `.env` file:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
3. (Optional) Set up Google Cloud services:
   - Create a Google Cloud project
   - Enable necessary APIs (Cloud Run, Cloud Storage)
   - Configure credentials and project settings in `.env`

## Quick Start

1. **Clone & Setup**
   ```bash
   git clone https://github.com/HarleyCoops/Math-To-Manim
   cd Math-To-Manim
   ```

2. **Environment Setup**
   ```bash
   # Create and configure .env file with your API keys
   cp .env.example .env
   # Edit .env with your API keys
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Launch Web Interface**
   ```bash
   python app.py
   ```
   This will start a Gradio web interface where you can interact with the AI models.

4. **Generate Animations**
   - Enter mathematical concepts or prompts in the chat interface
   - Select your preferred AI model (DeepSeek or Google Gemini)
   - The AI will generate Manim code for visualizing the concept
   - Use the generated code to create animations

## Rendering Animations

To render animations from generated code:

```bash
# Render a specific scene
python -m manim path/to/generated_file.py SceneName -pql  # Low quality for quick preview
python -m manim path/to/generated_file.py SceneName -pqh  # High quality for final output

# Run a presentation sequence
python run_presentation.py
```

## Important Note

This repository contains the **output files** of a mathematical animation generation process, not the complete pipeline. Users can run these files to render the animations on their machines, but the model and methodology used to generate these animation scripts are not included.

In other words, this repo provides the Manim code that produces the visualizations, but not the AI system that creates this code from mathematical concepts. The complete pipeline from mathematical concept to animation code remains proprietary.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

