# Animation First Learner README Design

Status: Approved

Date: July 24, 2026

## Goal

The root README should explain Math To Manim through its strongest visual
explainers, then help a learner, parent, teacher, or developer make one.

The page should feel like a premiere followed by a friendly guide. It should
not feel like an archive, a release log, or a provider comparison.

## Product Promise

The primary promise is:

> Ask a question. Get a visual explainer.

The short product definition is:

> Math To Manim turns a math or physics question into a carefully reasoned
> visual explanation. It works backward to identify what the learner needs to
> know, rebuilds those ideas in teaching order, checks the mathematics, and
> animates the explanation in Manim.

The Manim credit follows immediately:

> Manim is the open source animation engine originally created by Grant
> Sanderson for 3Blue1Brown. It powers many of the most recognizable math and
> physics animations online. This project uses the edition maintained by the
> Manim community.

The credit should link to the official Manim documentation.

## Editorial Rules

1. Call user facing outputs visual explainers or explainers.
2. Use scene, render, animation, and film only when discussing implementation
   details or existing file types.
3. Never use hyphens, en dashes, or em dashes in written prose.
4. Dashes remain valid when required by filenames, commands, code, links,
   identifiers, or markup syntax.
5. Write for a curious learner before writing for a pipeline developer.
6. Explain the learning outcome before naming an internal component.
7. Keep paragraphs short and concrete.
8. Every featured caption should say what is taught, what the learner sees,
   and why the visual helps.

## Root Page Structure

### Opening

Keep the star chart intact. Follow it with the title, the product promise,
essential badges, and a short navigation row.

### Featured Visual Explainers

Show six large explainers in this order:

1. Erdős 1038
2. The Jacobian Conjecture
3. The Traitor Axis
4. Vortex Leapfrog
5. The Valley of Stability
6. Exceptional Point Monodromy

Erdős 1038 remains the first animation. Its preview links to the complete MP4.
Its explanation remains the most expansive example because it demonstrates
the desired learner first voice.

The other five entries use one compact paragraph each. Deep mathematical
notes and long production prompts should be placed inside optional details
blocks or linked documents.

The section ends with one invitation to browse the full motion showcase.

### What Is Math To Manim

Place the product definition and Manim credit directly after the featured
explainers. Explain that this is not a template picker and not a direct jump
from a sentence to Python. The reasoning process is the product.

### What Can I Ask

Show a range of real prompts before installation instructions.

The examples should include:

1. Middle school arithmetic and algebra

   "Explain why a negative number times a negative number becomes positive to
   an eighth grade student. Use a number line, one everyday analogy, and one
   worked example."

2. Geometry

   "Show why the Pythagorean theorem works without assuming advanced algebra.
   Build the squares on all three sides and rearrange their areas."

3. Introductory algebra

   "Teach slope using three ramps. Explain rise over run, compare steepness,
   then solve one line equation."

4. High school physics

   "Explain conservation of momentum using two carts that collide. Show the
   momentum arrows before and after impact."

5. University mathematics

   "Explain Fourier series as rotating vectors that rebuild a signal. Begin
   with a circle and add one frequency at a time."

6. Research level mathematics

   "Show why one loop around an exceptional point swaps the eigenvalue
   branches. Assume I know complex numbers but not covering spaces."

Include a reusable prompt recipe:

> Explain [topic] to [learner]. Assume they already know [starting point].
> Use [visual metaphor or physical model]. Work through [specific example].
> End with [summary or check question].

The examples should make clear that the user can specify age, prior knowledge,
pace, visual style, worked examples, notation, and a final comprehension
check.

### How The Reasoning Pipeline Works

Present one provider neutral flow first:

1. Understand the learner and the real question.
2. Work backward to find every missing prerequisite.
3. Walk those prerequisites forward as a teaching sequence.
4. Select the definitions, equations, and examples that carry the idea.
5. Plan what appears on screen and how the camera reveals it.
6. Compose a complete Manim scene.
7. Validate the code and mathematical presentation.
8. Render, inspect, and repair the visual explainer.

Use a compact text flow or diagram. Avoid provider names in this first
explanation.

After the general flow, explain that the repository contains two independent
native implementations:

1. Mythos uses the Claude CLI and a six agent charter chain.
2. Sol uses the Codex CLI and durable specialist stages.

Neither implementation routes through the other.

Add a related architecture note after the two native implementations:

> Kimi uses an agent architecture that is different enough to warrant its own
> repository. Explore [Kimi K3 Manim](https://github.com/HarleyCoops/KimiK3Manim).

Do not imply that Kimi is a third implementation inside this repository.

### Make Your First Explainer

Present the easiest conversational path first.

#### MCP

Show the install command, the server command, and one client configuration.
Then show what a person can type in an MCP connected assistant:

> Use Math To Manim to create a visual explainer for my eighth grade student.
> Explain why solving an equation means doing the same thing to both sides.
> Use a balance scale, solve 3x + 5 = 20, and end with one practice question.

Explain the interaction in plain language:

1. The assistant starts the explainer.
2. The user can ask for progress.
3. The assistant can inspect the reasoning artifacts.
4. The final scene and render remain in the local run directory.

Keep the detailed MCP tool table lower on the page as reference.

#### Command Line

Show one Mythos command and one Sol command side by side in separate blocks.
State the login requirement before each command.

Mythos:

```bash
math-to-manim run "Explain fractions with a folding paper model for a sixth grade learner." --render -q m
```

Sol:

```bash
math-to-manim-sol run "Explain fractions with a folding paper model for a sixth grade learner."
```

The command line section should link to the full Sol contract and the Mythos
architecture details.

#### API

Keep the REST API as the path for applications and services. It should not
interrupt the beginner path.

### Technical Reference

After onboarding, retain concise sections for:

1. Installation and doctor checks
2. Run artifacts
3. MCP tools
4. REST routes
5. Configuration
6. Testing
7. Repository layout
8. License

Move provider specific architecture tables into clearly labeled sections.
Do not describe Mythos as the only engine.

## Material Removed From The Root

Remove these items from the root README:

1. The Last Day feature
2. The plate atlas sequence
3. The Associate Family feature
4. The Holonomy feature
5. The reverse reasoning and grammar preview pair
6. The policy geometry and field theory preview pair
7. All dense thumbnail rows
8. The duplicate motion showcase grid near the bottom
9. The long release announcement
10. The extended origin story

The animation assets remain in the repository. The full legacy collection
remains available through the motion showcase. A concise origin paragraph may
remain near the bottom of the root page with a link to historical material.

## Validation

Automated checks should verify:

1. Erdős 1038 is the first local GIF in the root README.
2. All six selected explainer assets are present and referenced.
3. The star chart remains present.
4. The Last Day asset is not referenced by the root README.
5. Legacy thumbnail grids are not referenced by the root README.
6. The motion showcase link remains present.
7. Both Mythos and Sol commands are present.
8. MCP setup and a natural language usage example are present.
9. At least one eighth grade example is present.
10. The product definition and Manim credit are present.
11. The Kimi K3 Manim repository is linked with an accurate separation note.
12. Prose added or rewritten by this change contains no dash punctuation.
13. Existing offline tests pass.

## Success Criteria

A new reader should be able to answer these questions without searching:

1. What does this product make?
2. Why is its output more thoughtful than direct text to code generation?
3. Can it explain middle school material?
4. What should I type?
5. How do I use it from an assistant through MCP?
6. How do I use it from a terminal?
7. What is the difference between Mythos and Sol?
8. Why does the Kimi architecture live in a separate repository?
9. Where can I find every older animation?
