"""Exercise an installed Astra wheel outside the source checkout, without model calls."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import venv


def check_wheel(wheel):
    scratch = Path(tempfile.mkdtemp(prefix='astra-wheel-'))
    environment = scratch / 'venv'
    venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    workspace = scratch / 'workspace'
    workspace.mkdir()
    env = {k: v for k, v in os.environ.items() if not any(
        word in k.upper() for word in ('API_KEY', 'SECRET', 'TOKEN', 'PASSWORD'))}
    env.pop('PYTHONPATH', None)
    # Use an isolated runtime cache, so an existing source install cannot satisfy setup.
    env['LOCALAPPDATA' if os.name == 'nt' else 'XDG_CACHE_HOME'] = str(scratch / 'cache')
    def run(*args, **kwargs):
        return subprocess.run([str(python), '-I', *args], cwd=workspace, env=env, check=True, **kwargs)
    run('-m', 'pip', 'install', str(wheel.resolve()) + '[mcp]')
    run('-c', "from pathlib import Path; from importlib.metadata import version; import astra; from astra.pipeline import Pipeline; "
        "assert astra.__version__ == version('math-to-manim'); "
        "assert Path(astra.__file__).is_relative_to(Path(__import__('sys').prefix)); "
        "assert Pipeline().runs_dir == Path.cwd()/'runs/astra'")
    for args in (('--version',), ('run', '--help'), ('setup', '--help'),
                 ('login', '--help'), ('serve-mcp', '--help'), ('runs',)):
        run('-m', 'astra.cli', *args)
    run('-m', 'astra.cli', 'design-map', '--stage', 'render', stdout=subprocess.DEVNULL)
    run('-c', "import asyncio; from astra.mcp_server import mcp; "
        "names={t.name for t in asyncio.run(mcp.list_tools())}; "
        "assert {'m2m_create_animation','m2m_get_job','m2m_list_runs','m2m_get_scene_code'} <= names")
    run('-m', 'astra.cli', 'setup')
    result = run('-c', "import json; from astra.client import BRIDGE; from astra.runtime import runtime_directory; "
                 "print(json.dumps({'bridge':str(BRIDGE),'runtime':str(runtime_directory())}))",
                 capture_output=True, text=True)
    paths = json.loads(result.stdout)
    subprocess.run(['node', '--check', paths['bridge']], cwd=workspace, env=env, check=True)
    check = subprocess.run(['node', paths['bridge'], '--check-runtime', paths['runtime']],
                           cwd=workspace, env=env, check=True, capture_output=True, text=True)
    assert json.loads(check.stdout) == {'model': 'gpt-6-astra', 'sdk_version': '0.156.1'}
    print(f'Astra wheel, MCP registration and locked SDK verified outside checkout: {scratch}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wheel', type=Path)
    check_wheel(parser.parse_args().wheel)
