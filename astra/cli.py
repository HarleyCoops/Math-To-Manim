"""Primary Math-To-Manim command: Astra specialists and jev at every checkpoint."""
import argparse
import json
from pathlib import Path
import subprocess
from astra import __version__
from astra.client import clean_environment
from astra.models import Request
from astra.pipeline import Pipeline, ROOT

def main(argv=None):
    p=argparse.ArgumentParser(prog='math-to-manim',description='Astra-native films with independent jev review at each step.')
    p.add_argument('--version',action='version',version=f'math-to-manim Astra {__version__}')
    commands=p.add_subparsers(dest='command',required=True)
    run=commands.add_parser('run');run.add_argument('prompt');run.add_argument('-q','--quality',choices=['l','m','h'],default='h')
    run.add_argument('--effort',choices=['high','xhigh','max'],default='high')
    run.add_argument('--max-revisions',type=int,default=6);run.add_argument('--no-render',action='store_true')
    resume=commands.add_parser('resume');resume.add_argument('run_dir',type=Path)
    rec=commands.add_parser('recommend',help='Ask real Jev to select a focused Astra investigation')
    rec.add_argument('run_dir',type=Path)
    rec.add_argument('--stage',choices=['brief','mathematics','storyboard','scene','render'],required=True)
    rec.add_argument('--attempt',type=int)
    rec.add_argument('--execute',action='store_true',help='Execute a sufficiently confident selection with Astra')
    rec.add_argument('--design',action='store_true',help='Evaluate the detailed artistic and teaching decision map first')
    design_map=commands.add_parser('design-map',help='Print the complete Jev design rubric without API calls')
    design_map.add_argument('--stage',choices=['brief','mathematics','storyboard','scene','render'])
    commands.add_parser('doctor')
    commands.add_parser('runs')
    args=p.parse_args(argv)
    if args.command=='design-map':
        from astra.design import mapping
        print(json.dumps(mapping(args.stage),indent=2))
        return 0
    if args.command=='recommend':
        from astra.actions import recommend
        print(json.dumps(recommend(args.run_dir,args.stage,args.attempt,args.execute,args.design),indent=2))
        return 0
    if args.command=='doctor':
        result=subprocess.run(['node',str(ROOT/'node_modules/@openai/codex/bin/codex.js'),'login','status'],env=clean_environment())
        for tool in ['ffmpeg','latex']:
            import shutil
            print(f'{tool}: {shutil.which(tool) or "missing"}')
        from astra.jev import load_api_key
        try:
            load_api_key()
            print('TypeSafe: credential configured (not a live authentication check)')
        except RuntimeError:
            print('TypeSafe: missing TYPESAFE_API_KEY')
            return 1
        return result.returncode
    if args.command=='runs':
        for path in sorted((ROOT/'runs/astra').glob('*/manifest.json')):
            data=json.loads(path.read_text());print(path.parent.name,data['status'])
        return 0
    if args.command=='resume':
        result=Pipeline().run(None,folder=args.run_dir)
    else:
        result=Pipeline().run(Request(prompt=args.prompt,quality=args.quality,effort=args.effort,
                                      max_revisions=args.max_revisions,render=not args.no_render))
    print(json.dumps(result,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
