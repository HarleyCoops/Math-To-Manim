"""Child-process environment for Codex, npm and the renderer: no credentials inherited."""
import os


def clean_environment():
    return {k: v for k, v in os.environ.items() if not any(
        word in k.upper() for word in ("API_KEY", "SECRET", "TOKEN", "PASSWORD"))}
