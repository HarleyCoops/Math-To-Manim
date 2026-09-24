"""One fresh Astra Codex SDK session per specialist or jev review."""
import json
import os
from pathlib import Path
import subprocess

BRIDGE = Path(__file__).with_name("bridge.mjs")
MODEL = "gpt-6-astra"

def clean_environment():
    return {k:v for k,v in os.environ.items() if not any(
        word in k.upper() for word in ("API_KEY", "SECRET", "TOKEN", "PASSWORD"))}

class CodexSDK:
    def call(self, prompt, *, cwd, output, schema, images=(), effort="high", search=False):
        output = Path(output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        trace = output.with_suffix(".trace.jsonl")
        payload = dict(prompt=prompt, cwd=str(Path(cwd).resolve()), output=str(output),
                       trace=str(trace), schema=schema.model_json_schema(),
                       images=[str(Path(p).resolve()) for p in images], effort=effort,
                       sandbox="read-only", search=search, timeoutMs=1800000)
        output.with_suffix(".prompt.txt").write_text(prompt, encoding="utf-8")
        result = subprocess.run(["node", str(BRIDGE)], input=json.dumps(payload),
                                text=True, encoding="utf-8", capture_output=True,
                                env=clean_environment(), timeout=1830)
        if result.returncode:
            raise RuntimeError(f"Codex SDK failed: {result.stderr[-3000:]}")
        if not output.is_file():
            raise RuntimeError("Codex SDK produced no structured result")
        output.with_suffix(".session.json").write_text(result.stdout, encoding="utf-8")
        return schema.model_validate_json(output.read_text(encoding="utf-8"))
