# Repository layout

Python packages live under `src/`; their import names and CLI commands are unchanged.
Dependency lists live under `requirements/`, and the Base44 Compose file lives in
`deployment/`. Examples, films, research materials, and historical implementations
retain their existing locations.

After updating an existing source checkout, refresh its editable installation from
the repository root in your usual Python environment:

```bash
python -m pip install -e . --no-deps
```

Run dependency installation from the repository root:

```bash
python -m pip install -r requirements/requirements.txt
```

For the local web preview:

```bash
docker compose -f deployment/docker-compose.base44.yml up -d
```

The Compose bind mount still points at the repository root. Run outputs remain in
`runs/`; package discovery, tests, runtime lookup, build scripts, and CI use the new
source layout. Existing local scripts that explicitly add the repository root to
`sys.path` should add its `src` directory instead, or use the editable installation.
