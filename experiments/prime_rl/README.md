# Prime Visual-Improvement Experiments

This directory owns reproducible experiment configuration and evidence for the
standalone `m2m2_visual_improvement` environment. Prime Hosted Training runs
the optimizer; this repository owns the tasks, environment, reward, launcher,
and result ledgers.

## Capability Preflight

The 2026-07-24 implementation preflight pinned:

- Prime CLI `0.6.20`;
- Verifiers `0.2.1`;
- CPython `3.12`;
- environment/image authorization: login required;
- hosted-training authorization: login with training scope required;
- `Qwen/Qwen3-VL-4B-Instruct` support: not yet verified because the cached API
  key is unauthorized for Hosted Training.

An authorization failure is not evidence that a model is unavailable. The
launcher must repeat this probe after `prime login` before publishing or
training.
