"""Render retained work without invoking any model or changing past review verdicts."""
from datetime import datetime, timezone
import json
from pathlib import Path
from astra.pipeline import digest, save
from astra.rendering import render, validate_source


def render_existing(run_dir, candidate, quality='m'):
    folder=Path(run_dir).resolve()
    candidate=Path(candidate).resolve()
    source=candidate.read_text(encoding='utf-8')
    if candidate.suffix=='.json':source=json.loads(source)['content']
    validate_source(source)
    ledger_path=folder/'manifest.json'
    ledger=json.loads(ledger_path.read_text())
    attempt=max([int(p.name) for p in (folder/'renders').glob('*') if p.name.isdigit()]+[0])+1
    ledger.update(status='rendering',error=None,review_mode='disabled_for_local_render',
                  review_status='not_reviewed',render_quality=quality)
    ledger.setdefault('events',[]).append(dict(stage='local_render',attempt=attempt,
        candidate=str(candidate),candidate_sha256=digest(candidate),quality=quality,
        reason='User requested no further Jev blockers or model spending. Local rendering only; no approval inferred.'))
    save(ledger_path,ledger)
    print(f'Local render at quality {quality}; no model or API calls',flush=True)
    try:
        video,frames,sheet=render(folder,source,quality,attempt)
        ledger.update(status='completed',video=video.relative_to(folder).as_posix(),
            video_sha256=digest(video),contact_sheet=sheet.relative_to(folder).as_posix(),
            rendered_source=(sheet.parent/'scene.py').relative_to(folder).as_posix(),
            completed_utc=datetime.now(timezone.utc).isoformat())
    except Exception as exc:
        ledger.update(status='failed',error=f'{type(exc).__name__}: {exc}')
        raise
    finally:save(ledger_path,ledger)
    return ledger
