"""Record independently computed illustration values for the pi paper film."""
import hashlib
import json
from pathlib import Path
import mpmath as mp


def main():
    paper = Path(__file__).resolve().parents[1] / 'papers/pi-approximations'
    mp.mp.dps = 80
    convergents = [(3, 1), (22, 7), (333, 106), (355, 113), (103993, 33102),
                  (104348, 33215), (208341, 66317), (312689, 99532)]
    rows = []
    for p, q in convergents:
        error = abs(mp.pi - mp.mpf(p) / q)
        assert error > 0 and error < mp.mpf(1) / q**2
        rows.append(dict(p=p, q=q, error=mp.nstr(error, 35),
                         quadratic_reference=mp.nstr(mp.mpf(1) / q**2, 35),
                         log10_q=mp.nstr(mp.log10(q), 25),
                         minus_log10_error=mp.nstr(-mp.log10(error), 25)))
    spikes = []
    for n in (3, 22, 333, 355, 1043):
        q = int(mp.nint(n / mp.pi))
        offset = n - q * mp.pi
        sine = abs(mp.sin(n))
        assert abs(sine - abs(mp.sin(offset))) < mp.mpf('1e-75')
        spikes.append(dict(n=n, nearest_multiple=q, offset=mp.nstr(offset, 35),
                           abs_sine=mp.nstr(sine, 35),
                           summand=mp.nstr(1 / (n**3 * sine**2), 35)))
    data = dict(precision_decimal_digits=80, convergents=rows, flint_hills=spikes,
                finite_partial_sum_1000=mp.nstr(mp.fsum(1 / (n**3 * mp.sin(n)**2)
                    for n in range(1, 1001)), 35),
                scope='Finite numerical illustrations; no research theorem verified.')
    (paper / 'computation.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    files = {}
    for path in sorted((paper / 'source').rglob('*')):
        if path.is_file():
            raw = path.read_bytes()
            record = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
            if path.suffix != '.pdf':
                record['lines'] = len(raw.splitlines())
            files[path.relative_to(paper).as_posix()] = record
    provenance = dict(upstream='https://github.com/openai/math',
        revision='fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb',
        manuscript='preprints/The-irrationality-exponent-of-pi-is-2-September-24-2026',
        date='2026-09-24', family='017', files=files,
        scope='Pinned source snapshot and finite arithmetic checks. Lean not executed.')
    (paper / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
