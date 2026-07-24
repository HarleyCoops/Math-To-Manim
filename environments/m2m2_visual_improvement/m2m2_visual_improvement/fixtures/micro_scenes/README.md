# Micro-scene fixtures

The executable fixture templates are defined in `micro_scenes.py`. Their
canonical, generated representations are committed in
`data/base_scenes.jsonl`; corrupted baselines are committed in
`data/tasks.jsonl`. Keeping generation in one module prevents hand-edited
fixtures from drifting away from the dataset hashes.
