"""Render retained work without invoking any model or changing past review verdicts."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from astra.rendering import FILM_DURATION, next_render_attempt, render, validate_source
from astra.runs import digest, save


LOCAL_RENDER_REASON='User requested no further Jev blockers or model spending. Local rendering only; no approval inferred.'


def render_existing(run_dir, candidate, quality='m', *, duration_range=FILM_DURATION, reason=LOCAL_RENDER_REASON):
    folder=Path(run_dir).resolve()
    candidate=Path(candidate).resolve()
    source=candidate.read_text(encoding='utf-8')
    if candidate.suffix=='.json':source=json.loads(source)['content']
    validate_source(source)  # Fail before the manifest records a render attempt.
    ledger_path=folder/'manifest.json'
    ledger=json.loads(ledger_path.read_text(encoding='utf-8'))
    attempt=next_render_attempt(folder)
    ledger.update(status='rendering',error=None,review_mode='disabled_for_local_render',
                  review_status='not_reviewed',render_quality=quality)
    ledger.setdefault('events',[]).append(dict(stage='local_render',attempt=attempt,
        candidate=str(candidate),candidate_sha256=digest(candidate),quality=quality,
        reason=reason))
    save(ledger_path,ledger)
    print(f'Local render at quality {quality}; no model or API calls',file=sys.stderr,flush=True)
    try:
        video,frames,sheet=render(folder,source,quality,attempt,duration_range=duration_range)
        metadata=json.loads((sheet.parent/'metadata.json').read_text(encoding='utf-8'))
        ledger.update(status='completed',video=video.relative_to(folder).as_posix(),
            video_sha256=digest(video),contact_sheet=sheet.relative_to(folder).as_posix(),
            rendered_source=(sheet.parent/'scene.py').relative_to(folder).as_posix(),
            duration_seconds=float(metadata['format']['duration']),
            completed_utc=datetime.now(timezone.utc).isoformat())
    except Exception as exc:
        ledger.update(status='failed',error=f'{type(exc).__name__}: {exc}')
        raise
    finally:save(ledger_path,ledger)
    return ledger
