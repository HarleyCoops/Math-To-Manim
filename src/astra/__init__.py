"""Astra-native mathematical film production through the official Codex SDK."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("math-to-manim")
except PackageNotFoundError:
    __version__ = "0+source"
