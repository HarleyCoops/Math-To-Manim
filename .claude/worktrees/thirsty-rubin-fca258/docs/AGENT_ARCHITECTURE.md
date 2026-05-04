# Multi-Agent Architecture Design
## Math-To-Manim v2.0

**Goal**: Transform `"explain cosmology"` -> professional Manim animation + study notes

---

## Core Philosophy

**Problem**: Current system requires 2000+ token verbose prompts with LaTeX expertise
**Solution**: Chain of specialized agents that each do one thing exceptionally well

**Key Insight**: What makes this work is the **Prompt Agent** - the critical innovation that bridges human language to LLM-ready verbose prompts.

---

## Architecture Overview

### Message Flow

```python
# User submits simple request
user_input = "Explain cosmology to me"

# Orchestrator routes through agents
orchestrator = AgentOrchestrator()
result = orchestrator.process(user_input)

# Behind the scenes:
"""
1. Concept Agent parses intent
   -> Output: {concepts: ["big bang", "expansion", "CMB"], level: "beginner"}

2. Research Agent gathers content
   -> Output: {formulas: [...], definitions: {...}, context: "..."}

3. Prompt Agent builds verbose prompt [*] CRITICAL STEP
   -> Output: 2000+ token LaTeX-rich prompt (this is what we're good at!)

4. Code Agent generates Manim
   -> Output: Python code using Manim Community Edition

5. Docs Agent creates study notes
   -> Output: LaTeX -> PDF

6. Quality Agent validates
   -> Output: Pass/Fail + suggestions

7. If pass: Render animation
   If fail: Loop back with improvements
"""
```

---

## Agent Specifications

### 1. Concept Agent
**Model**: DeepSeek R1 (reasoning capabilities)

**Input**: Raw user prompt (any length, any style)

**Output**: Structured JSON
```json
{
  "main_topic": "cosmology",
  "subtopics": ["big bang theory", "cosmic expansion", "CMB", "dark matter"],
  "complexity_level": "beginner",  // beginner | intermediate | advanced
  "estimated_duration": "5-7 minutes",
  "visual_elements": [
    "expanding universe simulation",
    "timeline of cosmic events",
    "CMB temperature fluctuations map"
  ],
  "prerequisites": ["basic physics", "understanding of spacetime"],
  "related_concepts": ["general relativity", "particle physics"]
}
```

**Prompt Template**:
```python
CONCEPT_EXTRACTION_PROMPT = """
You are an expert at analyzing educational requests.

User request: {user_input}

Extract the following:
1. Main mathematical/scientific concept
2. Key subtopics to cover
3. Appropriate complexity level (beginner/intermediate/advanced)
4. Suggested visual elements for animation
5. Prerequisites the viewer should have
6. Related concepts for context

Output as JSON.
"""
```

**Success Criteria**:
- Correctly identifies main topic 95%+ of the time
- Subtopic relevance score >0.8 (human evaluation)
- Complexity level matches user intent 90%+

---

### 2. Research Agent
**Model**: Gemini 2.5 (web search + multimodal)

**Input**: Concept Agent output (JSON)

**Output**: Knowledge base
```json
{
  "formulas": [
    {
      "name": "Friedmann Equation",
      "latex": "\\left(\\frac{\\dot{a}}{a}\\right)^2 = \\frac{8\\pi G}{3}\\rho - \\frac{kc^2}{a^2}",
      "description": "Describes expansion of the universe",
      "source": "General Relativity",
      "difficulty": "advanced"
    }
  ],
  "definitions": {
    "cosmic microwave background": "Thermal radiation from the early universe...",
    "redshift": "The stretching of light wavelengths due to cosmic expansion..."
  },
  "historical_context": "Edwin Hubble discovered cosmic expansion in 1929...",
  "key_figures": ["Hubble", "Friedmann", "Penzias & Wilson"],
  "citations": [
    {
      "type": "paper",
      "title": "A Relation Between Distance and Radial Velocity...",
      "authors": ["E. Hubble"],
      "year": 1929,
      "url": "..."
    }
  ],
  "visual_data": {
    "images": ["hubble_deep_field.jpg"],
    "diagrams": ["expansion_diagram.svg"]
  }
}
```

**Tools**:
- Web search (Wikipedia, arXiv, Wolfram Alpha)
- Formula databases (LaTeX Search, DLMF)
- Image search for visual references
- Citation lookup (Semantic Scholar API)

**Success Criteria**:
- All formulas compile in LaTeX
- Definitions are accurate (verified against sources)
- Citations are real and accessible
- Appropriate difficulty level

---

### 3. Prompt Agent [*]
**Model**: Fine-tuned DeepSeek R1 (trained on simple->verbose pairs)

**Input**:
- Concept Agent output (concepts)
- Research Agent output (formulas, definitions)
- User preferences (duration, style, level)

**Output**: Verbose 2000+ token prompt
```python
# Example output (abbreviated)
"""
Begin by slowly fading in a panoramic starfield backdrop representing the observable
universe. As the camera pans across this cosmic vista, introduce a large title reading
'Cosmology: The Story of Our Universe' written in bold, glowing text at the center.

[... 1800 more tokens of detailed instructions ...]

Use the Friedmann equation:
$$\\left(\\frac{\\dot{a}}{a}\\right)^2 = \\frac{8\\pi G}{3}\\rho - \\frac{kc^2}{a^2}$$

Display this equation on a semi-transparent plane, with each term color-coded:
- $\\dot{a}/a$ (Hubble parameter) in cyan
- $\\rho$ (energy density) in orange
- $k$ (curvature) in purple

[... more detailed animation instructions ...]
"""
```

**Training Data**:
```python
# Format: List of (simple, verbose) pairs
training_examples = [
    {
        "simple": "Show the Pythagorean theorem",
        "verbose": "Begin with a square of side length a+b. Construct four identical...",
        "metadata": {
            "success": True,
            "render_time": "45s",
            "user_rating": 4.8,
            "complexity": "beginner"
        }
    },
    # ... 500+ more examples from our existing successful animations
]
```

**Fine-tuning Strategy**:
1. **Phase 1**: Supervised learning on successful (simple -> verbose) pairs
2. **Phase 2**: RLHF using render success as reward signal
3. **Phase 3**: Iterative improvement from user feedback

**Critical Features**:
- **LaTeX expertise**: Knows how to format math for Manim
- **Visual storytelling**: Sequences animations logically
- **Pacing**: Balances detail with watchability
- **Color theory**: Suggests complementary color schemes
- **Accessibility**: Includes verbal descriptions, clear labels

**Success Criteria**:
- 80%+ of generated verbose prompts produce working Manim code
- Average prompt length: 1500-2500 tokens
- LaTeX syntax error rate <5%
- Human evaluation: "Would use this verbatim" >70%

---

### 4. Code Agent
**Model**: DeepSeek R1 (proven excellent at code generation)

**Input**: Verbose prompt from Prompt Agent

**Output**: Manim Python code
```python
from manim import *

class CosmologyExplainer(Scene):
    def construct(self):
        # Title sequence
        title = Text("Cosmology: The Story of Our Universe")
        title.scale(1.5)
        self.play(FadeIn(title))
        self.wait(2)
        self.play(title.animate.to_edge(UP))

        # Starfield background
        stars = self.create_starfield()
        self.add(stars)

        # Friedmann equation
        equation = MathTex(
            r"\left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2}"
        )
        # ... hundreds more lines

    def create_starfield(self):
        # Helper method for starfield
        ...
```

**Current Status**: [DONE] **Already works well!** This is our strong point.

**Enhancements Needed**:
- Better error handling
- More helper functions library
- Optimization for render time
- Accessibility features (audio descriptions)

**Success Criteria**:
- 95%+ code runs without syntax errors
- 90%+ renders successfully
- Average render time <10 minutes
- Code is readable and well-commented

---

### 5. Docs Agent
**Model**: Gemini 2.5 (excellent at natural language)

**Input**:
- Original user request
- Concept + Research data
- Generated Manim code
- Rendered animation (video file)

**Output**: LaTeX document -> PDF
```latex
\documentclass{article}
\usepackage{amsmath, graphicx, hyperref}

\title{Study Notes: Cosmology}
\author{Generated by Math-To-Manim}
\date{\today}

\begin{document}
\maketitle

\section{Introduction}
Cosmology is the study of the universe's origin, evolution, and structure...

\section{The Friedmann Equation}
The expansion of the universe is governed by:
\begin{equation}
\left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{kc^2}{a^2}
\end{equation}

Where:
\begin{itemize}
\item $a(t)$ is the scale factor...
\item $\rho$ is the energy density...
\end{itemize}

[... detailed explanations ...]

\section{Visualizations}
See the accompanying animation for:
- Timeline of cosmic events
- CMB temperature map
- Expansion simulation

\section{Further Reading}
\begin{itemize}
\item Hubble, E. (1929). "A Relation Between Distance..."
\end{itemize}

\end{document}
```

**Success Criteria**:
- LaTeX compiles to PDF 100% of the time
- Explanations are pedagogically sound (teacher review)
- Matches complexity level from Concept Agent
- Integrates with animation seamlessly

---

### 6. Quality Agent
**Model**: Claude Opus or GPT-4o (critical thinking)

**Input**: Everything from all previous agents

**Output**: Quality report + suggestions
```json
{
  "validation": {
    "latex_syntax": {
      "status": "pass",
      "errors": [],
      "warnings": ["Consider using \\dfrac instead of \\frac for readability"]
    },
    "manim_code": {
      "status": "pass",
      "linter_results": "No issues found",
      "estimated_render_time": "8 minutes",
      "suggestions": [
        "Consider caching the starfield for faster renders",
        "Animation at line 145 could be 0.5s faster"
      ]
    },
    "mathematical_accuracy": {
      "status": "pass",
      "formula_checks": [
        {
          "formula": "Friedmann equation",
          "verified": true,
          "source": "Carroll & Ostlie, Modern Astrophysics"
        }
      ],
      "concerns": []
    },
    "accessibility": {
      "status": "warning",
      "color_contrast": "PASS (WCAG AA)",
      "colorblind_friendly": "PASS (Deuteranopia safe)",
      "recommendations": [
        "Add audio narration track",
        "Increase subtitle font size by 10%"
      ]
    },
    "pedagogical_quality": {
      "status": "pass",
      "pacing_score": 8.5,
      "clarity_score": 9.0,
      "engagement_score": 8.0,
      "notes": "Excellent progression from simple to complex"
    }
  },
  "overall_verdict": "APPROVED",
  "confidence": 0.92,
  "recommended_actions": [
    "Apply colorblind-friendly palette",
    "Add 2 more examples of redshift"
  ]
}
```

**Validation Tools**:
- LaTeX linter (ChkTeX)
- Python linter (pylint, black)
- Math verification (SymPy symbolic checking)
- Accessibility checker (WCAG tools)
- Render simulator (estimates time/memory)

**Success Criteria**:
- False positive rate <5%
- Catches 95%+ of critical errors
- Suggestions are actionable
- Turnaround time <30 seconds

---

## Orchestrator: The Conductor

### State Machine

```python
from enum import Enum
from typing import Dict, Any

class PipelineState(Enum):
    INIT = "init"
    CONCEPT_EXTRACTION = "concept_extraction"
    RESEARCH = "research"
    PROMPT_GENERATION = "prompt_generation"
    CODE_GENERATION = "code_generation"
    DOCS_GENERATION = "docs_generation"
    QUALITY_CHECK = "quality_check"
    RENDERING = "rendering"
    COMPLETE = "complete"
    FAILED = "failed"

class AgentOrchestrator:
    def __init__(self):
        self.state = PipelineState.INIT
        self.context = {}  # Shared state across agents
        self.agents = self._initialize_agents()

    def process(self, user_input: str) -> Dict[str, Any]:
        """Main orchestration logic"""
        try:
            # 1. Concept extraction
            self.state = PipelineState.CONCEPT_EXTRACTION
            concepts = self.agents['concept'].extract(user_input)
            self.context['concepts'] = concepts

            # 2. Research
            self.state = PipelineState.RESEARCH
            knowledge = self.agents['research'].gather(concepts)
            self.context['knowledge'] = knowledge

            # 3. Prompt generation [*]
            self.state = PipelineState.PROMPT_GENERATION
            verbose_prompt = self.agents['prompt'].expand(
                concepts=concepts,
                knowledge=knowledge,
                user_input=user_input
            )
            self.context['verbose_prompt'] = verbose_prompt

            # 4. Code generation
            self.state = PipelineState.CODE_GENERATION
            manim_code = self.agents['code'].generate(verbose_prompt)
            self.context['code'] = manim_code

            # 5. Documentation
            self.state = PipelineState.DOCS_GENERATION
            docs = self.agents['docs'].create(
                context=self.context,
                animation_code=manim_code
            )
            self.context['docs'] = docs

            # 6. Quality check
            self.state = PipelineState.QUALITY_CHECK
            qa_result = self.agents['quality'].validate(self.context)

            if qa_result['overall_verdict'] != 'APPROVED':
                # Retry logic with improvements
                return self._handle_failure(qa_result)

            # 7. Render
            self.state = PipelineState.RENDERING
            video_path = self._render_animation(manim_code)
            pdf_path = self._compile_latex(docs)

            self.state = PipelineState.COMPLETE
            return {
                'status': 'success',
                'animation': video_path,
                'study_notes': pdf_path,
                'code': manim_code,
                'qa_report': qa_result
            }

        except Exception as e:
            self.state = PipelineState.FAILED
            return self._handle_error(e)

    def _handle_failure(self, qa_result: Dict) -> Dict:
        """Retry with improvements from QA agent"""
        # Implementation: Loop back to appropriate agent with fixes
        pass

    def _handle_error(self, error: Exception) -> Dict:
        """Graceful error handling"""
        # Log, notify, return useful error message
        pass
```

### Retry Strategy

```python
MAX_RETRIES = 3

retry_logic = {
    'concept_extraction': 'Use different model or ask user for clarification',
    'research': 'Fall back to cached knowledge or broader search',
    'prompt_generation': 'Simplify scope or use template fallback',
    'code_generation': 'Apply QA suggestions and regenerate',
    'quality_check': 'Manual review queue for edge cases'
}
```

---

## Inter-Agent Communication

### Message Protocol

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
import uuid

@dataclass
class AgentMessage:
    message_id: str = str(uuid.uuid4())
    from_agent: str
    to_agent: str
    task_id: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime = datetime.now()
    priority: str = "normal"  # low | normal | high | urgent

    def to_json(self) -> str:
        return json.dumps({
            'message_id': self.message_id,
            'from_agent': self.from_agent,
            'to_agent': self.to_agent,
            'task_id': self.task_id,
            'payload': self.payload,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority
        })

# Example usage
msg = AgentMessage(
    from_agent='concept_agent',
    to_agent='research_agent',
    task_id='task-12345',
    payload={
        'concepts': ['cosmology', 'big bang'],
        'detail_level': 'intermediate'
    },
    metadata={
        'user_id': 'user-789',
        'session_id': 'session-456'
    },
    priority='high'
)
```

---

## Technology Stack

### Core Framework
- **LangGraph**: Agent orchestration (from LangChain team)
- **LangChain**: LLM integrations & tools
- **Manim Community Edition**: Animation rendering

### LLM Providers
- **DeepSeek R1**: Concept, Prompt, Code agents
- **Gemini 2.5**: Research, Docs agents
- **Claude Opus / GPT-4o**: Quality agent

### Supporting Tools
- **Redis**: Message queue & caching
- **PostgreSQL**: Prompt history, user data
- **S3/R2**: Video & PDF storage
- **Gradio**: Web interface
- **FastAPI**: REST API (future)

### Monitoring
- **Weights & Biases**: ML experiment tracking
- **Sentry**: Error tracking
- **Prometheus + Grafana**: Performance metrics
- **LangSmith**: LLM call tracing

---

## Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| **End-to-end latency** | <5 minutes | User attention span |
| **Success rate** | >80% | Good enough for v1 |
| **Cost per animation** | <$0.50 | Sustainable at scale |
| **Prompt expansion quality** | >4.0/5 | User satisfaction |
| **Code correctness** | >90% | Minimize frustration |

---

## Next Steps

1. **This Week**:
   - [ ] Set up LangGraph project
   - [ ] Implement Concept Agent (simplest)
   - [ ] Create sample messages & tests

2. **Next 2 Weeks**:
   - [ ] Build Prompt Agent (critical path)
   - [ ] Collect training data for fine-tuning
   - [ ] Start smolagents integration

3. **Month 1**:
   - [ ] All 6 agents functional
   - [ ] Basic orchestrator working
   - [ ] End-to-end demo with 5 examples

4. **Month 2-3**:
   - [ ] Fine-tune Prompt Agent
   - [ ] Add retry logic & error handling
   - [ ] Build web UI for multi-step workflow
   - [ ] Community testing

---

## Open Questions

1. **Agent granularity**: Should we split Research into Formula + Context agents?
2. **Model selection**: Can we use smaller models for some agents?
3. **Caching strategy**: When to cache vs. regenerate?
4. **User control**: How much visibility/control over each agent?
5. **Fallbacks**: What if an agent consistently fails?

---

**Last Updated**: 2025-10-02
**Version**: 1.0 (Draft)
**Maintainer**: @HarleyCoops
