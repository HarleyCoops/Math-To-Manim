# DeepSeek-Manim Animation Generator

## Author's Note

I originally wrote this repository before DeepSeek published their official API. As such, you can ignore the Colab notebook and Hugging Face model download instructions - they're obsolete now that DeepSeek has released their API!

## Quick Start

1. Clone this repository
2. Create a `.env` file and add your DeepSeek API key:
   ```
   DEEPSEEK_API_KEY=your_api_key_here
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Gradio interface:
   ```bash
   python app.py
   ```
5. Use the chat interface to ask DeepSeek to create any Manim animation
6. Copy the returned Python script to a new .py file
7. Run the animation using Manim's CLI

## Running Manim Animations

### Basic Command Structure
might need to install libs manim need:(ubuntu) `sudo apt-get install -y libcairo2-dev pkg-config python3-dev libpangocairo-1.0-0 libpango1.0-dev`
```bash
python -m manim [flags] your_script.py SceneName
```
The `SceneName` must match the name of the scene class defined in your script. For example, in my case, R1 returned a class called `class QEDJourney(ThreeDScene):`, then you would use:
```bash
python -m manim [flags] QED.py QEDJourney
```

### Quality Options
- `-ql` (480p, fastest, best for development)
- `-qm` (720p, good balance)
- `-qh` (1080p, high quality)
- `-qk` (4K, very high quality)

### Preview Options
- `-p` Preview the animation when done
- `-f` Show the output file in file browser

### Partial Rendering
When debugging or resuming after an error, you can render specific parts of your animation:
```bash
# Start from a specific animation number
python -m manim -qh --from-animation 11 your_script.py SceneName

# Render a specific range of animations
python -m manim -qh --from-animation 11 --upto-animation 15 your_script.py SceneName
```
This is particularly useful for:
- Resuming after errors without re-rendering everything
- Debugging specific sections of your animation
- Saving time during development

### Output Formats
- Default: MP4
- `-i` Output as GIF
- `--format VIDEO` Choose format (mp4, mov, gif, webm)

### Output Location
All rendered animations are saved in:
```
media/videos/[script_name]/[quality]/[scene_name].[format]
```

### Development Tips
1. Use `-pql` during development for quick previews
2. Use `-qh` for final renders
3. Add `-f` to easily locate output files
4. Use `--format gif` for easily shareable animations

For example:
```bash
# During development (preview QEDJourney scene from QED.py in low quality)
python -m manim -pql QED.py QEDJourney

# Final render (render QEDJourney scene from QED.py in high quality)
python -m manim -qh QED.py QEDJourney
```

---

# Original Documentation Below

## **Animating QED with Manim: A Test Case of Open Models**

**DeepSeek R1-Zero** is a custom, instruction-tuned large language model (LLM) designed for advanced reasoning and knowledge completion tasks. Although it derives conceptual inspiration from Google's T5 framework, it features **substantial architectural modifications** allowing for an extended context window, refined attention mechanisms, and robust performance across zero-shot and few-shot paradigms.

---

## **Table of Contents**

1. [Introduction](#introduction)  
2. [Philosophical & Theoretical Foundations](#philosophical--theoretical-foundations)  
3. [Model Architecture](#model-architecture)  
4. [Installation & Quickstart](#installation--quickstart)  
5. [Quantization & Memory Footprint](#quantization--memory-footprint)  
6. [Implementation Details](#implementation-details)  
7. [Performance Benchmarks](#performance-benchmarks)  
8. [Potential Limitations & Future Work](#potential-limitations--future-work)  
9. [Usage Examples](#usage-examples)  
10. [Citation](#citation)  
11. [License & Usage Restrictions](#license--usage-restrictions)  

---

## **1. Introduction**

DeepSeek R1-Zero represents the culmination of **multi-year research** at DeepSeek AI into **transfer learning**, **instruction tuning**, and **long-context neural architectures**. Its central objective is to provide a single, all-purpose encoder-decoder model that can handle:

- **Complex reading comprehension** (up to 8,192 tokens)  
- **Scenario-based instruction following** (e.g., "Given a set of constraints, produce a short plan.")  
- **Technical and coding tasks** (including code generation, transformation, and debugging assistance)  

Though R1-Zero is a "descendant" of T5, the modifications to attention, context management, and parameter initialization distinguish it significantly from vanilla T5 implementations.

---

## **2. Philosophical & Theoretical Foundations**

While standard Transformer models rely on the "Attention is All You Need" paradigm (Vaswani et al., 2017), **DeepSeek R1-Zero** extends this by:

1. **Expanded Context Window**  
   - By employing distributed positional encodings and segment-based attention, R1-Zero tolerates sequences up to 8,192 tokens.  
   - The extended context window leverages **blockwise local attention** (in certain layers) to mitigate quadratic scaling in memory usage.

2. **Instruction Tuning**  
   - Similar to frameworks like FLAN-T5 or InstructGPT, R1-Zero was exposed to curated prompts (instructions, Q&A, conversation) to improve zero-shot and few-shot performance.  
   - This approach helps the model produce more stable, context-aware answers and reduces "hallucination" events.

3. **Semantic Compression**  
   - The encoder can compress textual segments into "semantic slots," enabling more efficient cross-attention in the decoder stage.  
   - This is theoretically grounded in **Manifold Hypothesis** arguments, where the textual input can be seen as lying on a lower-dimensional manifold, thus amenable to a compressed representation.

From a **cognitive science** perspective, R1-Zero aspires to mimic a layered approach to knowledge assimilation, balancing short-term "working memory" (sequence tokens) with long-term "knowledge representation" (model parameters).

---

## **3. Model Architecture**

### **3.1 Summary of Structural Modifications**

- **Parameter Count**: ~6.7B  
- **Encoder-Decoder**: Maintains T5's text-to-text approach but with specialized gating and partial reordering in cross-attention blocks.  
- **Context Window**: 8,192 tokens (a 4× expansion over many standard T5 models).  
- **Layer Stacking**: The modifications allow some dynamic scheduling of attention heads, facilitating better throughput in multi-GPU environments.

### **3.2 Detailed Specifications**

| Aspect                      | Specification                                     |
|----------------------------|---------------------------------------------------|
| **Architecture Type**      | Modified T5 (custom config named `deepseek_v3`)  |
| **Heads per Attention**    | 32 heads (in deeper layers)                      |
| **Layer Count**            | 36 encoder blocks, 36 decoder blocks             |
| **Vocabulary Size**        | 32k tokens (SentencePiece-based)                 |
| **Positional Encoding**    | Absolute + Learned segment-based for 8k tokens   |
| **Training Paradigm**      | Instruction-tuned + Additional domain tasks      |
| **Precision**              | FP32, FP16, 4-bit, 8-bit quantization (via BnB)  |

---

## **4. Installation & Quickstart**

Below are **simplified** instructions for installing DeepSeek R1-Zero:

### **4.1 Requirements**

- **Python** >= 3.8  
- **PyTorch** >= 2.0  
- **Transformers** >= 4.34.0  
- **Accelerate** >= 0.24.0  
- **bitsandbytes** >= 0.39.0 (if using 4-bit/8-bit)

### **4.2 Installing via `pip`**

```bash
pip install --upgrade torch transformers accelerate bitsandbytes
```

If your environment's default PyTorch is older than 2.0, consider updating or installing from PyPI/conda channels that provide a recent version.

### **4.3 Model Download**

After installing prerequisites, you can load the model from the [Hugging Face Hub](https://huggingface.co/deepseek-ai/DeepSeek-R1-Zero). For example:

```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained(
    "deepseek-ai/DeepSeek-R1-Zero",
    trust_remote_code=True
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    "deepseek-ai/DeepSeek-R1-Zero",
    trust_remote_code=True,
    torch_dtype=torch.float16,   # or torch.float32
    device_map="auto"           # automatically move model to GPU if available
)
```

> **Note**:  
> 1) `trust_remote_code=True` is essential because R1-Zero uses custom code.  
> 2) Download times may be substantial (potentially hours) depending on your bandwidth and how Hugging Face shards large models.

---

## **5. Quantization & Memory Footprint**

DeepSeek R1-Zero supports **multi-bit quantization** to optimize memory usage:

1. **4-Bit Quantization**  
   - **Pros**: Minimizes VRAM usage (~8GB).  
   - **Cons**: Potentially minor losses in numeric accuracy or generative quality.

2. **8-Bit Quantization**  
   - **Pros**: Still significantly reduces memory (~14GB VRAM).  
   - **Cons**: Slight overhead vs. 4-bit but often better fidelity.

3. **Full Precision (FP32)**  
   - **Pros**: The highest theoretical accuracy.  
   - **Cons**: ~28GB VRAM usage, not feasible on smaller GPUs.

Sample quantized load (4-bit) with [bitsandbytes](https://github.com/TimDettmers/bitsandbytes):

```python
model_4bit = AutoModelForSeq2SeqLM.from_pretrained(
    "deepseek-ai/DeepSeek-R1-Zero",
    trust_remote_code=True,
    device_map="auto",
    load_in_4bit=True
)
```

---

## **6. Implementation Details**

### **6.1 Memory Management**

- **Sharded Checkpoints**: The model is split into multiple shards; each shard is verified upon download. Large shards can be memory-mapped, so your system requirements also include disk I/O overhead.  
- **Accelerate Integration**: By leveraging [Accelerate](https://github.com/huggingface/accelerate), you can distribute model shards across multiple GPUs or perform CPU offloading if GPU memory is insufficient.

### **6.2 Extended Context Mechanism**

- **Rotary & Segment Encodings**: At large sequence lengths, standard absolute positions can degrade performance. R1-Zero's hybrid approach (inspired by [T5], [LongT5], and [RoFormer]) helps maintain stable gradients even at 8k tokens.  
- **Parallel Cross-Attention**: The decoder employs a specialized parallel cross-attention mechanism in certain layers, which can reduce overhead in multi-GPU setups.

---

## **7. Performance Benchmarks**

**DeepSeek R1-Zero** typically competes near GPT-3.5 performance in standard generative benchmarks:

- **Inference Latency**  
  - 4-bit: ~100–200ms per token (varies by GPU)  
  - FP16: ~200–400ms per token  
  - FP32: ~400–800ms per token

- **Quality Metrics**  
  - **BLEU & ROUGE**: On summarization tasks (CNN/DailyMail), R1-Zero hovers at ~1–2 points below GPT-3.5.  
  - **Open Domain QA**: On NaturalQuestions, R1-Zero closely matches strong baselines (e.g., T5-XXL) when properly instructed.

Keep in mind that your hardware setup and parallelism strategies can influence these benchmarks significantly.

---

## **8. Potential Limitations & Future Work**

Despite R1-Zero's strengths, several **limitations** persist:

1. **Token Context Limit**: 8,192 tokens is high, but certain extreme use cases (e.g., full-text searching in large documents) may require bridging or chunking.  
2. **Training Biases**: While instruction-tuning reduces hallucinations, domain gaps remain. For heavily specialized or newly emerging knowledge, the model may produce uncertain or dated information.  
3. **Interpretability**: Like all Transformer-based LLMs, R1-Zero functions as a "black box." Advanced interpretability tools are still an active research area.

**Future Directions**:  
- Integrating advanced memory systems to handle prompts beyond 8k tokens.  
- Incorporating **flash attention** for further speed-ups.  
- Investigating retrieval-augmented generation modules to reduce outdated knowledge reliance.

---

## **9. Usage Examples**

Below are a few quick examples to illustrate R1-Zero's capabilities:

### **9.1 Short Story Generation**

```python
prompt = "Write a short sci-fi story about artificial intelligence."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
output_ids = model.generate(inputs["input_ids"], max_length=150)
print(tokenizer.decode(output_ids[0], skip_special_tokens=True))
```

### **9.2 Technical Explanation**

```python
prompt = "Explain the concept of gradient descent as if speaking to a first-year PhD student."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
output_ids = model.generate(inputs["input_ids"], max_length=200)
print(tokenizer.decode(output_ids[0], skip_special_tokens=True))
```

Feel free to refine these prompts and tune generation parameters (`num_beams`, `temperature`, `top_k`, etc.) to shape the style.

---

## **10. Citation**

If you use this project in your research or work, please cite it as:

```bibtex
@misc{cooper2025deepseekmanim,
    title={DeepSeek-Manim Animation Generator: Automated Mathematical Animations using DeepSeek API},
    author={Cooper, Christian H.},
    year={2025},
    howpublished={\url{https://github.com/HarleyCoops/Deepseek-R1-Zero}},
    note={A tool for generating Manim animations using DeepSeek's API}
}
```





