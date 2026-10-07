"""Cloud render of an Astra-authored candidate, with no model credentials or calls."""
import argparse
from pathlib import Path

from astra.local_render import render_existing
from astra.pipeline import digest, save
from astra.rendering import validate_source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--quality', choices=['l', 'm', 'h'], default='m')
    args = parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    candidate=args.candidate.resolve()
    output=args.output.resolve()
    if root/'papers' not in candidate.parents or root/'runs/astra' not in output.parents:
        raise ValueError('Candidate must be in papers/ and output in runs/astra/')
    import json
    source=candidate.read_text(encoding='utf-8')
    if candidate.suffix=='.json':
        source=json.loads(source)['content']
    validate_source(source)
    output.mkdir(parents=True,exist_ok=False)
    save(output/'manifest.json', dict(status='queued',model='gpt-6-astra',
        evaluator='disabled',review_status='not_reviewed',events=[],
        source_candidate=candidate.relative_to(root).as_posix(),
        source_candidate_sha256=digest(candidate),execution='cloud_render_existing'))
    render_existing(output,candidate,args.quality)


if __name__=='__main__':
    main()
