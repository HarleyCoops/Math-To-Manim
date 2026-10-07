"""Retain an exact completed Astra scene and its provenance for cloud rendering."""
import argparse
import json
from pathlib import Path
import shutil

from astra.client import MODEL
from astra.models import Artifact, STAGES
from astra.pipeline import ROOT, digest, save
from astra.rendering import validate_source


def export_candidate(paper, run_dir, *, root=ROOT):
    root = Path(root).resolve()
    paper = Path(paper).resolve()
    run_dir = Path(run_dir).resolve()
    if paper.parent != root / 'papers' or not paper.is_dir():
        raise ValueError('Expected an existing paper folder directly under papers/')
    if run_dir.parent != root / 'runs/astra' or not run_dir.is_dir():
        raise ValueError('Expected an Astra run directly under runs/astra/')
    ledger = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
    if ledger.get('status') != 'completed' or ledger.get('model') != MODEL:
        raise ValueError('Only completed Astra authoring can be exported')
    for stage in STAGES:
        hashes = ledger.get('stages', {}).get(stage, {}).get('hashes', {})
        if f'{stage}.json' not in hashes or 'request.json' not in hashes:
            raise ValueError(f'Missing source bindings for {stage}')
        for name, expected in hashes.items():
            path = (run_dir / name).resolve()
            if run_dir not in path.parents or not path.is_file() or digest(path) != expected:
                raise ValueError(f'Changed or invalid source binding: {name}')

    scene = run_dir / 'scene.json'
    artifact = Artifact.model_validate_json(scene.read_text(encoding='utf-8'))
    validate_source(artifact.content)
    audits = []
    audited_stages = set()
    for path in sorted((run_dir / 'attempts').glob('*-astra-audit.json')):
        record = path.with_suffix('.record.json')
        if not record.is_file():
            raise ValueError(f'Missing audit bindings: {path.name}')
        binding = json.loads(record.read_text(encoding='utf-8'))
        assessment = json.loads(path.read_text(encoding='utf-8'))
        if binding.get('model') != MODEL or binding.get('role') != 'astra-evidence-auditor':
            raise ValueError(f'Unexpected audit model or role: {path.name}')
        for name, expected in binding.get('input_hashes', {}).items():
            evidence = (run_dir / name).resolve()
            if run_dir not in evidence.parents or not evidence.is_file() or digest(evidence) != expected:
                raise ValueError(f'Changed or invalid audit evidence: {name}')
            for stage in STAGES:
                if name.endswith(f'-{stage}-candidate.json') and expected == digest(run_dir / f'{stage}.json'):
                    audited_stages.add(stage)
        audits.append({
            'file': path.relative_to(run_dir).as_posix(),
            'sha256': digest(path),
            'binding': binding,
            'assessment': assessment,
        })
    if audited_stages != set(STAGES):
        raise ValueError('Every exported stage must have a bound Astra evidence audit')
    candidate = paper / 'candidate.json'
    shutil.copyfile(scene, candidate)
    # No machine paths, login material, raw SDK traces or session identifiers.
    provenance = {
        'run_id': run_dir.name,
        'model': MODEL,
        'authoring_status': 'completed',
        'review_mode': ledger.get('review_mode'),
        'review_status': ledger.get('review_status'),
        'film_status': 'pending_cloud_render',
        'completed_utc': ledger.get('completed_utc'),
        'candidate_sha256': digest(candidate),
        'stage_bindings': ledger['stages'],
        'astra_audits': audits,
        'limitations': [
            'Completed authoring is not evidence of a completed film.',
            'Cloud render-existing output is not_reviewed until actual evidence is inspected.',
            'Astra scores are uncalibrated model judgments, not independent proof certificates.',
        ],
    }
    save(paper / 'production.json', provenance)
    return {'run_id': run_dir.name, 'candidate': candidate.relative_to(root).as_posix(),
            'candidate_sha256': provenance['candidate_sha256']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paper', type=Path)
    parser.add_argument('run_dir', type=Path)
    args = parser.parse_args()
    print(json.dumps(export_candidate(args.paper, args.run_dir), indent=2))


if __name__ == '__main__':
    main()
