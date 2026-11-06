"""Primary Math-To-Manim command: Astra specialists and jev at every checkpoint."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
from astra import __version__
from astra.environment import clean_environment
from astra.models import CHECKPOINTS, EFFORTS, QUALITIES, REVIEW_MODES, Request
from astra.pipeline import Pipeline
from astra.runs import list_runs
from astra.runtime import setup_runtime, codex_command

def main(argv=None):
    p=argparse.ArgumentParser(prog='math-to-manim',description='Astra-native films with independent jev review at each step.')
    p.add_argument('--version',action='version',version=f'math-to-manim Astra {__version__}')
    commands=p.add_subparsers(dest='command',required=True)
    commands.add_parser('setup',help='Install the pinned Astra Codex runtime')
    commands.add_parser('login',help='Sign in to Codex with ChatGPT')
    run=commands.add_parser('run');run.add_argument('prompt');run.add_argument('-q','--quality',choices=QUALITIES,default='h')
    run.add_argument('--effort',choices=EFFORTS,default='high')
    run.add_argument('--max-revisions',type=int,default=6);run.add_argument('--no-render',action='store_true')
    run.add_argument('--review-mode',choices=REVIEW_MODES,default='advisory')
    local=commands.add_parser('render-existing',help='Render saved scene code with zero model/API calls')
    local.add_argument('run_dir',type=Path)
    local.add_argument('--candidate',type=Path,required=True,help='Saved candidate JSON or scene Python file')
    local.add_argument('-q','--quality',choices=QUALITIES,default='m')
    resume=commands.add_parser('resume');resume.add_argument('run_dir',type=Path)
    resume.add_argument('-q','--quality',choices=QUALITIES,help='Override delivery quality while preserving approved mathematical planning')
    rec=commands.add_parser('recommend',help='Ask real Jev to select a focused Astra investigation')
    rec.add_argument('run_dir',type=Path)
    rec.add_argument('--stage',choices=CHECKPOINTS,required=True)
    rec.add_argument('--attempt',type=int)
    rec.add_argument('--execute',action='store_true',help='Execute a sufficiently confident selection with Astra')
    rec.add_argument('--design',action='store_true',help='Evaluate the detailed artistic and teaching decision map first')
    design_map=commands.add_parser('design-map',help='Print the complete Jev design rubric without API calls')
    design_map.add_argument('--stage',choices=CHECKPOINTS)
    doctor=commands.add_parser('doctor')
    doctor.add_argument('--review-mode',choices=REVIEW_MODES,default='advisory')
    commands.add_parser('runs')
    server=commands.add_parser('serve-mcp',help='Serve the Astra SDK / TypeSafe Jev MCP connection')
    server.add_argument('--transport',choices=['stdio','streamable-http'],default='stdio')
    server.add_argument('--port',type=int,default=8644)
    args=p.parse_args(argv)
    if args.command=='setup':
        print(f'Codex runtime installed: {setup_runtime()}')
        print('Authenticate with: math-to-manim login')
        return 0
    if args.command=='login':
        return subprocess.run(codex_command('login'),env=clean_environment()).returncode
    if args.command=='serve-mcp':
        from astra.mcp_server import main as serve  # needs the optional mcp extra
        serve(args.transport,args.port)
        return 0
    if args.command=='render-existing':
        from astra.local_render import render_existing
        print(json.dumps(render_existing(args.run_dir,args.candidate,args.quality),indent=2))
        return 0
    if args.command=='design-map':
        from astra.design import mapping
        print(json.dumps(mapping(args.stage),indent=2))
        return 0
    if args.command=='recommend':
        from astra.recommend import recommend
        print(json.dumps(recommend(args.run_dir,args.stage,args.attempt,args.execute,args.design),indent=2))
        return 0
    if args.command=='doctor':
        try:
            result=subprocess.run(codex_command('login','status'),env=clean_environment())
        except RuntimeError as exc:
            print(str(exc))
            return 1
        for tool in ['ffmpeg','latex']:
            print(f'{tool}: {shutil.which(tool) or "missing"}')
        if args.review_mode=='off':
            print('TypeSafe: disabled by request; no credential needed')
            return result.returncode
        from astra.jev import load_api_key
        try:
            load_api_key()
            print('TypeSafe: credential configured (not a live authentication check)')
        except RuntimeError:
            print('TypeSafe: missing TYPESAFE_API_KEY')
            return 1
        return result.returncode
    if args.command=='runs':
        for name,manifest in list_runs():print(name,manifest['status'])
        return 0
    if args.command=='resume':
        result=Pipeline().run(None,folder=args.run_dir,render_quality=args.quality)
    else:
        result=Pipeline().run(Request(prompt=args.prompt,quality=args.quality,effort=args.effort,
                                      max_revisions=args.max_revisions,render=not args.no_render,
                                      review_mode=args.review_mode))
    print(json.dumps(result,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
