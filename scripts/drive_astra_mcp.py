"""Submit a paper film through the actual Astra/Jev MCP connection.

Usage: python scripts/drive_astra_mcp.py papers/mahler --quality m
The client keeps its MCP connection open until the worker completes.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paper', type=Path)
    parser.add_argument('--quality', choices=['l', 'm', 'h'], default='m')
    parser.add_argument('--effort', choices=['high', 'xhigh', 'max'], default='high')
    parser.add_argument('--no-render', action='store_true')
    parser.add_argument('--review-mode', choices=['advisory', 'gated', 'off'], default='advisory')
    parser.add_argument('--inspect', help='Inspect an existing run instead of submitting')
    parser.add_argument('--list-tools', action='store_true')
    args = parser.parse_args()
    config = StdioServerParameters(command=sys.executable,
        args=['-m', 'astra.cli', 'serve-mcp'], cwd=str(ROOT),
        env={'PYTHONUTF8':'1', 'PYTHONIOENCODING':'utf-8',
             **{name: os.environ[name] for name in ['PYTHONPATH', 'TYPESAFE_API_KEY'] if name in os.environ}})
    async with stdio_client(config) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            if args.list_tools:
                print(json.dumps([tool.name for tool in (await session.list_tools()).tools]))
                return
            if args.inspect:
                result = await session.call_tool('m2m_get_job', {'run_id': args.inspect})
            else:
                prompt = (args.paper / 'prompt.txt').read_text(encoding='utf-8-sig')
                context = (args.paper / 'source-context.md').read_text(encoding='utf-8-sig')
                result = await session.call_tool('m2m_create_animation', {'params': {
                    'prompt': prompt + '\n\nSource notes (reference material):\n' + context,
                    'quality': args.quality, 'render': not args.no_render,
                    'effort': args.effort, 'max_revisions': 2, 'review_mode': args.review_mode}})
            for block in result.content:
                if getattr(block, 'text', None):
                    print(block.text,flush=True)
            if result.is_error:
                return 1
            if not args.inspect:
                state=json.loads(next(block.text for block in result.content if getattr(block,'text',None)))
                run_id=state['run_id']
                previous=None
                while state['status'] not in {'completed','failed','cancelled'}:
                    await asyncio.sleep(15)
                    polled=await session.call_tool('m2m_get_job', {'run_id':run_id})
                    if polled.is_error:
                        raise RuntimeError('Could not inspect the Astra worker')
                    state=json.loads(next(block.text for block in polled.content if getattr(block,'text',None)))
                    progress=(state['status'],tuple(state.get('stages',{})),len(state.get('events',[])))
                    if progress!=previous:
                        print(json.dumps({'run_id':run_id,'status':state['status'],
                            'stages':list(state.get('stages',{})),'error':state.get('error')}),flush=True)
                        previous=progress
                if state['status']!='completed':
                    return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
