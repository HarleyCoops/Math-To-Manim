# Vercel Skills Integration Research

## What is Vercel Skills (skills.sh)?

**Vercel Skills** is an open-source "package manager for AI coding agents" launched by Vercel in January 2026. It provides a standardized way to package, distribute, and install capabilities for AI coding assistants.

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **CLI Tool** | `npx skills` - the package manager |
| **Registry** | [skills.sh](https://skills.sh) - central discovery hub |
| **Format** | SKILL.md files with YAML frontmatter |
| **Adoption** | 20K+ installs within 6 hours of launch |
| **Scope** | 25+ supported AI coding agents |

### Supported Agents

The platform supports a wide range of AI coding assistants:
- **Claude Code** (Anthropic)
- **Codex** (OpenAI)
- **Cursor**
- **Opencode**
- **Cline**
- **Gemini**
- And 20+ more agents

---

## How It Works

### 1. Skill Structure

A skill is a directory containing:

```
my-skill/
├── SKILL.md           # Required: Instructions + metadata
├── scripts/           # Optional: Helper commands
└── references/        # Optional: Additional documentation
```

### 2. SKILL.md Format

```markdown
---
name: skill-name
description: Brief description of what this skill does
---

# Skill Title

Instructions for the AI agent to follow...

## When to Use
- Trigger condition 1
- Trigger condition 2

## Steps
1. First action
2. Second action
```

### 3. Installation Methods

```bash
# From GitHub shorthand
npx skills add HarleyCoops/Math-To-Manim

# From full GitHub URL
npx skills add https://github.com/HarleyCoops/Math-To-Manim

# Direct path to skill folder
npx skills add https://github.com/HarleyCoops/Math-To-Manim/tree/main/skill/skills/math-to-manim

# Local path
npx skills add ./Math-To-Manim/skill

# Target specific agents
npx skills add HarleyCoops/Math-To-Manim -a claude-code -a cursor
```

### 4. Discovery Commands

```bash
# Interactive search
npx skills find

# Keyword search
npx skills find manim

# List skills in a repo
npx skills add HarleyCoops/Math-To-Manim --list

# Check for updates
npx skills check

# Update all skills
npx skills update
```

---

## Integration Strategy for Math-To-Manim

### Current State

The Math-To-Manim project **already has a skill structure** that is compatible with Vercel Skills:

```
Math-To-Manim/
└── skill/
    ├── .claude-plugin/plugin.json    # Claude-specific manifest
    └── skills/math-to-manim/
        ├── SKILL.md                  # Main skill definition
        ├── references/               # Supporting documentation
        │   ├── reverse-knowledge-tree.md
        │   ├── agent-system-prompts.md
        │   ├── verbose-prompt-format.md
        │   └── manim-code-patterns.md
        └── examples/
            └── pythagorean-theorem/  # Complete example
```

### Gap Analysis

| Aspect | Current State | Required for Vercel Skills |
|--------|---------------|---------------------------|
| SKILL.md format | Compliant | Compliant |
| Name field | "Math-To-Manim" | Should be lowercase: "math-to-manim" |
| Description | Present | Present |
| Directory structure | `/skill/skills/math-to-manim/` | Standard paths expected |
| References | Present | Supported |

### Required Adaptations

#### 1. Skill Name Normalization
The name in SKILL.md should be lowercase with hyphens:
```yaml
---
name: math-to-manim  # Already correct!
description: ...
---
```

#### 2. Directory Structure Options

Vercel Skills CLI searches these paths in order:
1. `skills/`
2. `.agents/skills/`
3. `.claude/skills/`
4. `.cursor/skills/`

**Recommendation**: Move or symlink the skill to a standard location:
```bash
# Option A: Move to root skills/ directory
mkdir -p skills
mv skill/skills/math-to-manim skills/

# Option B: Create symlink
ln -s skill/skills skills
```

#### 3. Multi-Agent Compatibility

The current skill is Claude-focused. For broader agent support:
- Remove Claude-specific hooks (if any)
- Use generic markdown instructions
- Avoid `context: fork` directives (Claude/Cline only)

---

## Integration Options

### Option 1: Minimal Integration (Recommended)

Just ensure the skill is discoverable:

1. **Restructure directories**:
   ```
   Math-To-Manim/
   └── skills/
       └── math-to-manim/
           ├── SKILL.md
           ├── references/
           └── examples/
   ```

2. **Users install via**:
   ```bash
   npx skills add HarleyCoops/Math-To-Manim
   ```

3. **Search on skills.sh**:
   The skill becomes searchable at `skills.sh/?q=manim`

### Option 2: Full Ecosystem Integration

Create a dedicated skills repository:

```bash
# Create separate repo
# github.com/HarleyCoops/math-to-manim-skill

math-to-manim-skill/
├── skills/
│   ├── math-to-manim/
│   │   └── SKILL.md
│   ├── manim-basics/
│   │   └── SKILL.md
│   └── reverse-knowledge-tree/
│       └── SKILL.md
└── README.md
```

### Option 3: Contribute to Vercel's Collection

Submit a PR to `vercel-labs/agent-skills` with the Math-To-Manim skill for maximum visibility.

---

## Implementation Checklist

- [ ] Rename `skill/` directory to `skills/` at repo root
- [ ] Verify SKILL.md frontmatter is valid
- [ ] Test installation: `npx skills add ./Math-To-Manim --list`
- [ ] Test with multiple agents: `-a claude-code -a cursor`
- [ ] Verify skill appears in search: `npx skills find manim`
- [ ] Document installation in README.md
- [ ] (Optional) Submit to vercel-labs/agent-skills

---

## Benefits of Integration

1. **Discoverability**: Users searching for "manim" on skills.sh will find Math-To-Manim
2. **Easy Installation**: One command: `npx skills add HarleyCoops/Math-To-Manim`
3. **Multi-Agent Support**: Works with Claude, Cursor, Codex, and 20+ other agents
4. **Update Mechanism**: `npx skills update` pulls latest version
5. **Ecosystem Presence**: Part of the growing AI agent skills ecosystem

---

## Technical Details

### CLI Architecture

The skills CLI:
1. Detects installed AI agents automatically
2. Parses GitHub/GitLab/local paths
3. Installs via symlink (preferred) or copy
4. Maintains lock file for version tracking
5. Supports update checking via API

### Search Functionality (skills.sh)

The website at `skills.sh/?q=manim` queries:
- Skill names
- Descriptions
- Keywords from SKILL.md

For optimal discoverability, include relevant keywords in the description:
```yaml
description: Transform mathematical concepts into Manim animations using AI.
  Supports physics, calculus, linear algebra, and more. Uses reverse knowledge
  tree algorithm for pedagogically sound visualizations.
```

### Environment Variables

```bash
# Disable telemetry
DISABLE_TELEMETRY=1

# Install internal/hidden skills
INSTALL_INTERNAL_SKILLS=1

# Skip agent detection
SKIP_AGENT_DETECTION=1
```

---

## Sources

- [Vercel Labs Skills GitHub](https://github.com/vercel-labs/skills)
- [Vercel Agent Skills Collection](https://github.com/vercel-labs/agent-skills)
- [Skills NPM Package](https://www.npmjs.com/package/skills)
- [Vercel Changelog - Introducing Skills](https://vercel.com/changelog/introducing-skills-the-open-agent-skills-ecosystem)
- [Apidog - How to Use Vercel Agent Skills](https://apidog.com/blog/vercel-agent-skills/)
