# GPT-5.6 Sol silo

## Boundary

The repository now contains two provider-native products:

| Silo | Runtime shape | Entry points |
|---|---|---|
| `mythos/` | Anthropic-native charter chain through Claude CLI turns | `math-to-manim`, `mythos.api` |
| `sol/` | OpenAI Responses API, GPT-5.6 Sol, hosted Python, typed scene contract | `math-to-manim-sol`, `sol.api` |

Neither silo calls the other's provider client, prompts, agents, or
orchestrator. Improvements can be evaluated independently without collapsing
both providers into their least-common-denominator abstraction.

## Sol pipeline

```text
problem
  -> GPT-5.6 Sol Responses API
     -> hosted Python calculation and verification
     -> strict CalculationResult JSON schema
  -> deterministic Manim compiler
  -> optional local render
```

The former Anthropic pipeline is not modified or deprecated by this work.

## Native tool choices

- `gpt-5.6-sol` is explicit so an alias cannot silently change the baseline.
- The Responses API is the only model endpoint.
- Code Interpreter is available to every live calculation and the system
  prompt requires it for nontrivial work.
- Structured Outputs forms the trust boundary. Sol returns mathematical and
  visual intent, never executable Manim.
- The Manim compiler rejects dangerous LaTeX commands and owns all Python.
- The API sends a stable, privacy-preserving `safety_identifier`.
- A small AST-based symbolic fallback supports arithmetic, linear equations,
  and real quadratics for CI and installations without a key.

Programmatic Tool Calling is intentionally absent from the first calculator:
one hosted calculation tool is a direct-call task, and its result needs fresh
model judgment. It becomes valuable when reference retrieval, asset selection,
and render inspection form a bounded multi-tool batch.

Multi-agent is also intentionally absent from the core path because the steps
are sequentially dependent. A future proof-verification mode can use
independent subagents without changing the calculator contract.

## Run it

```bash
pip install -e ".[api,render]"
export OPENAI_API_KEY=...

math-to-manim-sol calculate "solve x^2 - 5x + 6 = 0"
math-to-manim-sol calculate "solve 3x + 11 = 14" --offline
math-to-manim-sol serve --port 8656
```

The live endpoint is `POST /v1/calculate`. Runs are written to `runs/sol/`;
the Anthropic ledger remains `runs/mythos/`.
