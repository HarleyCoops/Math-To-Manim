# M2M2 Visual Improvement

This standalone Verifiers environment trains a multimodal policy to improve
already-valid Math-To-Manim renders. A rollout receives an immutable
educational contract, editable scene artifacts, and baseline visual evidence.
It returns one typed visual revision, which is rendered and compared with the
baseline.

The environment is intentionally separate from the provider-native `mythos`
and `sol` packages.
