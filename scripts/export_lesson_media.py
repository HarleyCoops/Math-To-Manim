"""Export a completed, Jev-approved run to the curated lesson showcase."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def export(run_dir: Path):
    run_dir = run_dir.resolve()
    manifest = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
    review = json.loads((run_dir / 'review.json').read_text(encoding='utf-8'))
    if manifest['status'] != 'completed' or review.get('evaluator') != 'jev' or review['status'] != 'approved':
        raise ValueError('Export requires a completed run with an approved Jev review')
    video = (run_dir / manifest['video_path']).resolve()
    video.relative_to(run_dir)
    record = json.loads((run_dir / review['record']).read_text(encoding='utf-8'))
    for name, digest in record['input_hashes'].items():
        path = (run_dir / name).resolve()
        path.relative_to(run_dir)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Reviewed evidence changed: {name}')
    assets = ROOT / 'docs/showcase/assets'
    target = assets / 'the-third-side.mp4'
    # Normalize the MP4 for immediate browser playback without re-encoding.
    subprocess.run(['ffmpeg','-y','-i',str(video),'-c','copy','-movflags','+faststart',str(target)], check=True, capture_output=True)
    subprocess.run(['ffmpeg','-y','-i',str(target),'-filter_complex',
        '[0:v]fps=15,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a',
        '-loop','0',str(assets / 'the-third-side.gif')], check=True, capture_output=True)
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(target)]))
    duration = float(probe['format']['duration'])
    subprocess.run(['ffmpeg','-y','-ss',str(max(0,duration-2)),'-i',str(target),'-frames:v','1',str(assets / 'the-third-side-poster.png')], check=True, capture_output=True)
    scene_dir = ROOT / 'examples/sol'
    scene_dir.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(run_dir / 'sol_scene.py', scene_dir / 'the_third_side.py')
    evidence_dir = ROOT / 'docs/showcase/the-third-side'
    evidence_dir.mkdir(exist_ok=True)
    shutil.copyfile(run_dir / '04_math_dossier.json', evidence_dir / 'math-dossier.json')
    shutil.copyfile(run_dir / 'review_frames/contact_sheet.png', evidence_dir / 'review-contact-sheet.png')
    stream = next(s for s in probe['streams'] if s['codec_type']=='video')
    summary = {
        'title':'The Third Side', 'run_id':manifest['run_id'],
        'writer_model':manifest['model'], 'reviewer_model':record['model'],
        'review_status':review['status'], 'assessment':review['assessment'],
        'score_kind':review['score_kind'],
        'duration_seconds':duration,'resolution':[stream['width'],stream['height']],
        'fps':stream['r_frame_rate'], 'video_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'scene_sha256':hashlib.sha256((scene_dir / 'the_third_side.py').read_bytes()).hexdigest(),
        'review_completed_utc':record['completed_utc'],
        'supervision_notes':json.loads((run_dir / 'supervision_notes.json').read_text(encoding='utf-8')) if (run_dir / 'supervision_notes.json').is_file() else [],
        'review_attempts':[
            {'attempt':r['attempt'], 'status':r['status'], 'error':r.get('error'),
             'verdict':json.loads(p.with_name('review.json').read_text(encoding='utf-8'))['status'] if p.with_name('review.json').is_file() else None}
            for p in sorted((run_dir / 'jev').glob('*/record.json'))
            for r in [json.loads(p.read_text(encoding='utf-8'))]
        ],
        'note':'Assessment citations refer to local run artifacts; sampled stills do not certify continuous motion.'
    }
    (evidence_dir / 'production.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir',type=Path)
    export(parser.parse_args().run_dir)
