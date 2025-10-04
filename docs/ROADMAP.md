# Math-To-Manim Roadmap
## Vision: Multi-Agent Animation Generation System

**Powered by**: Claude Sonnet 4.5 + Claude Agent SDK (October 2025)

**Goal**: Transform simple human prompts like "explain cosmology to me" into professional Manim Community Edition animations through an orchestrated multi-agent system built on the Claude Agent SDK.

---

## Current State (v0.9 - 1000[*])

[DONE] **Working**: Verbose prompts -> Claude Sonnet 4.5 -> Manim code -> Animations
[DONE] **AI Model**: Claude Sonnet 4.5 (claude-sonnet-4.5-20251022)
[DONE] **Framework**: Claude Agent SDK (open source, October 2025)
[DONE] **Output**: Animations + LaTeX study notes
[DONE] **Interface**: Gradio web UI ([app_claude.py](app_claude.py))
[DONE] **Examples**: 40+ working animation scripts

**Key Achievement**: Proven that 2000+ token verbose prompts + Claude Sonnet 4.5 generate high-quality Manim code

---

## Architecture Vision: The Agent Pipeline

```
┌─────────────────┐
│  Human Input    │ "Explain cosmology"
│  Simple Prompt  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              AGENT ORCHESTRATOR                         │
│         (Coordinates all agents below)                  │
└────────┬───────────────────────────────────────────┬────┘
         │                                           │
         ▼                                           ▼
┌─────────────────┐                         ┌─────────────────┐
│  CONCEPT AGENT  │                         │  QUALITY AGENT  │
│  - Extracts key │                         │  - Reviews all  │
│    concepts     │                         │    outputs      │
│  - Identifies   │                         │  - Validates    │
│    topics       │                         │    LaTeX/code   │
│  - Plans scope  │                         │  - Suggests     │
└────────┬────────┘                         │    improvements │
         │                                  └─────────────────┘
         ▼
┌─────────────────┐
│  RESEARCH AGENT │
│  - Gathers math │
│    details      │
│  - Formulas     │
│  - Definitions  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PREREQ EXPLORER │ [*] Core Innovation
│  - Asks "what   │
│    before X?"   │
│  - Builds tree  │
│    recursively  │
│  - Foundation->  │
│    target       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   CODE AGENT    │
│  - Generates    │
│    Manim code   │
│  - Uses verbose │
│    prompt       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   DOCS AGENT    │
│  - Creates      │
│    study notes  │
│  - LaTeX PDF    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Final Output   │ Animation + Docs
└─────────────────┘
```

---

## Phase 1: Foundation (Months 1-2)
**Status**: In Progress

### 1.1 Repository Professionalization
- [x] Update model names to latest versions
- [x] Create ROADMAP.md and architecture docs
- [ ] Create proper project structure
- [ ] Add comprehensive testing suite
- [ ] Set up CI/CD pipeline
- [ ] Community guidelines & templates

### 1.2 Core Infrastructure
- [ ] Agent base class framework
- [ ] Message passing system between agents
- [ ] Shared memory/context management
- [ ] Error handling & retry logic
- [ ] Logging & monitoring

### 1.3 Reverse Knowledge Tree System (Priority)
- [ ] Implement Prerequisite Explorer (recursive agent)
- [ ] Build Concept Analyzer (parse user intent)
- [ ] Create Narrative Composer (tree -> verbose prompt)
- [ ] Test on diverse topics (math, physics, CS)
- [ ] Validation tools for LaTeX

**Key Innovation**: No training data needed! Agents recursively ask "What must I understand BEFORE this?" to build knowledge trees from foundation -> target concept.

**See**: [REVERSE_KNOWLEDGE_TREE.md](REVERSE_KNOWLEDGE_TREE.md) for complete technical specification.

**Deliverable**: Working system that expands "explain X" -> complete knowledge tree -> 2000+ token verbose prompt

---

## Phase 2: Agent Ecosystem (Months 3-4)
**Status**: Planned

### 2.1 Concept Extraction Agent
**Purpose**: Parse human intent from simple prompts

**Capabilities**:
- Topic identification ("cosmology" -> big bang, expansion, CMB, dark matter)
- Scope determination (introduction vs. deep dive)
- Prerequisite detection (what math background needed)
- Visual element suggestions (what to animate)

**Tech Stack**: Claude Agent SDK + Claude Sonnet 4.5 for reasoning

### 2.2 Research Agent
**Purpose**: Gather authoritative mathematical content

**Capabilities**:
- Formula lookup (Wikipedia, arXiv, Wolfram)
- Definition retrieval
- Historical context
- Related concepts mapping
- Citation management

**Tech Stack**: Claude Agent SDK tools + Model Context Protocol (MCP) for external services

### 2.3 Code Generation Agent
**Purpose**: Convert verbose prompts -> Manim code

**Capabilities**:
- Manim API expertise
- LaTeX rendering in Manim
- Animation timing & pacing
- Color scheme selection
- Error handling for common issues

**Current Status**: Works well with Claude Sonnet 4.5! Use existing pipeline with enhanced capabilities.

### 2.4 Documentation Agent
**Purpose**: Generate study materials

**Capabilities**:
- LaTeX document generation
- Concept explanations
- Formula derivations
- Bibliography compilation
- PDF rendering

**Current Status**: Partially working, needs enhancement

### 2.5 Quality Assurance Agent
**Purpose**: Review and validate all outputs

**Capabilities**:
- LaTeX syntax validation
- Manim code linting
- Mathematical accuracy checking
- Accessibility review (color blindness, etc.)
- Performance optimization suggestions

---

## Phase 3: Orchestration (Months 5-6)
**Status**: Planned

### 3.1 Agent Orchestrator
**Purpose**: Coordinate agent workflow

**Responsibilities**:
- Route tasks to appropriate agents
- Manage agent dependencies
- Handle parallel processing
- Aggregate results
- Retry failed tasks
- Optimize agent selection based on task

### 3.2 State Management
- Conversation history
- Intermediate results caching
- User preference storage
- Version control for prompts/code
- Feedback loop integration

### 3.3 UI/UX Enhancements
- Multi-step progress visualization
- Agent activity dashboard
- Interactive prompt refinement
- Preview before rendering
- Export options (code, PDF, video)

---

## Phase 4: Intelligence & Learning (Months 7-9)
**Status**: Future

### 4.1 Reinforcement Learning Pipeline
**Goal**: Self-improving system from user feedback

**Components**:
- Success/failure tracking
- User rating collection
- Automated testing of generated code
- Model fine-tuning on successful examples
- A/B testing of different approaches

### 4.2 Multi-Model Strategy
**Goal**: Use the right model for each agent

**Mapping**:
- **Concept Agent**: DeepSeek R1 (reasoning)
- **Research Agent**: Gemini 2.5 (web search integration)
- **Prompt Agent**: Fine-tuned DeepSeek or Claude
- **Code Agent**: DeepSeek R1 (proven for this task)
- **Docs Agent**: Gemini 2.5 (natural language)
- **QA Agent**: GPT-4o or Claude Opus (critical thinking)

### 4.3 Advanced Features
- Voice input ("explain quantum mechanics")
- Image input (sketch -> animation)
- Interactive parameter tuning
- Real-time preview
- Collaborative editing
- Animation templates library

---

## Phase 5: Community & Scale (Months 10-12)
**Status**: Future

### 5.1 Community Platform
- Animation gallery
- Prompt sharing marketplace
- Leaderboard for best animations
- Educational curriculum integration
- Teacher/student accounts

### 5.2 API & Integrations
- REST API for external tools
- Jupyter notebook plugin
- VS Code extension
- Obsidian plugin for notes -> animations
- LMS integrations (Canvas, Moodle)

### 5.3 Performance & Scale
- Distributed rendering
- Cloud deployment options
- Rate limiting & quotas
- Caching strategies
- CDN for video delivery

---

## Technical Decisions

### Agent Framework
**Choice**: Claude Agent SDK (from Anthropic)

**Rationale**:
- Purpose-built by Anthropic for Claude-powered agents
- Built-in context management with automatic compaction
- Native tool ecosystem (file ops, code execution, web search)
- Model Context Protocol (MCP) for external service integration
- Subagent support for parallel processing
- Fine-grained permissions control
- Production-ready (powers Claude Code)
- Open source (October 2025)
- Active development by Anthropic team

**Advantages over alternatives**:
- Native Claude integration (optimized prompts, caching)
- No additional framework overhead
- Built-in best practices from Claude Code
- Superior context management

### Communication Protocol
**Choice**: Structured JSON messages

```json
{
  "from_agent": "concept_agent",
  "to_agent": "research_agent",
  "task_id": "uuid-1234",
  "payload": {
    "concepts": ["big bang", "cosmic inflation"],
    "detail_level": "intermediate",
    "formulas_needed": true
  },
  "metadata": {
    "timestamp": "2025-10-02T10:00:00Z",
    "priority": "high"
  }
}
```

### Data Storage
- **Prompts**: PostgreSQL (structured queries)
- **Animations**: S3/R2 (object storage)
- **Metadata**: Redis (fast lookup)
- **Feedback**: TimescaleDB (time-series analysis)

---

## Success Metrics

### Phase 1
- [ ] Prompt Agent achieves 80%+ success rate (verbose -> working code)
- [ ] Average prompt expansion: simple (50 tokens) -> verbose (2000+ tokens)
- [ ] Community engagement: 50+ contributors

### Phase 2
- [ ] Full agent pipeline: simple -> animation in <5 minutes
- [ ] Quality score: 90%+ animations render without errors
- [ ] Documentation completeness: 100% of animations have study notes

### Phase 3
- [ ] User satisfaction: 4.5+ stars average
- [ ] Scalability: Handle 1000+ concurrent requests
- [ ] Cost efficiency: <$0.50 per animation generated

---

## Open Questions & Research Needed

1. **Agent Communication**: Synchronous vs. async messaging?
2. **Failure Handling**: How many retries? Fallback strategies?
3. **Cost Optimization**: Which agents can use smaller/cheaper models?
4. **Prompt Caching**: Can we cache partial verbose prompts?
5. **Animation Quality**: Objective metrics beyond "it renders"?
6. **Math Validation**: How to verify correctness of formulas?
7. **Licensing**: Generated code ownership? User contributions?

---

## Resources Needed

### Development
- 2 full-time engineers (agent orchestration, Manim expertise)
- 1 ML engineer (smolagents fine-tuning)
- 1 designer (UI/UX for multi-step workflows)

### Infrastructure
- GPU cluster for training (H100 recommended)
- API credits: DeepSeek, Gemini, Anthropic
- Storage: 500GB+ for examples & cache
- Monitoring: DataDog or similar

### Community
- Discord server moderation
- Documentation writing
- Example curation
- Educational partnerships

---

## Getting Involved

### For Contributors
1. **Easy**: Add examples to the gallery
2. **Medium**: Improve prompt templates
3. **Hard**: Build individual agents
4. **Expert**: Design orchestration system

### For Researchers
- Fine-tuning experiments
- Multi-model ensemble strategies
- Animation quality metrics
- Mathematical validation

### For Educators
- Curriculum integration
- Use case studies
- Student feedback
- Pedagogical best practices

---

## Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| 1: Foundation | 2 months | Working Prompt Agent |
| 2: Agents | 2 months | 5+ specialized agents |
| 3: Orchestration | 2 months | End-to-end pipeline |
| 4: Intelligence | 3 months | Self-improving system |
| 5: Community | 3 months | Public platform |

**Total**: 12 months to full production system

---

## Next Steps (This Week)

1. [x] Update model names
2. [x] Create ROADMAP.md and architecture documentation
3. [ ] Finalize roadmap with community input
4. [ ] Create issues for Phase 1 tasks
5. [ ] Set up project board
6. [ ] Announce roadmap to community
7. [ ] Start building Prompt Agent training dataset

---

## Contributing to This Roadmap

This is a living document! To suggest changes:
1. Open an issue with tag `roadmap`
2. Join Discord #roadmap-discussion
3. Submit PR for concrete proposals

**Last Updated**: 2025-10-02
**Status**: Draft v1.0
**Maintainer**: @HarleyCoops
