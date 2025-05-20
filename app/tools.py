"""Secure code-exec sandbox tools."""

import os
import uuid
import tempfile
import subprocess
from textwrap import dedent

def run_python(code: str, globals_dict: dict = None, timeout: int = 2):
    """
    Execute Python code in a Docker sandbox with resource limits.

    Returns a dict with:
      - stdout: captured standard output
      - stderr: captured standard error
      - exit_code: process return code (None if timed out)
      - timeout: True if execution timed out
    """
    # Disallow banned modules via static analysis
    import ast
    banned = {'os', 'sys', 'subprocess', 'socket', 'shutil', 'pathlib', 'requests', 'urllib'}
    try:
        tree = ast.parse(code)
    except SyntaxError:
        pass
    else:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if mod in banned:
                        return {'stdout': '', 'stderr': f"ImportError: module '{mod}' is banned\n", 'exit_code': 1, 'timeout': False}
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split('.')[0]
                    if mod in banned:
                        return {'stdout': '', 'stderr': f"ImportError: module '{mod}' is banned\n", 'exit_code': 1, 'timeout': False}
    # Prepare restricted builtins
    allowed = ['print', 'len', 'sum', 'min', 'max', 'range', 'enumerate']
    builtins_map = ', '.join(f"'{name}': {name}" for name in allowed)
    header = dedent(f"""
        # restrict builtins
        __builtins__ = {{{builtins_map}}}
    """)
    # Prepare globals injection
    globals_code = ''
    if globals_dict:
        for k, v in globals_dict.items():
            globals_code += f"{k} = {repr(v)}\n"
    # Combine script
    script = header + '\n' + globals_code + '\n' + code
    # Ensure Docker image is available locally (pull if needed)
    image = 'python:3.12-slim'
    try:
        info = subprocess.run(
            ['docker', 'image', 'inspect', image],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if info.returncode != 0:
            subprocess.run(['docker', 'pull', image], check=True)
    except Exception:
        pass
    # Create temp workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, 'script.py')
        with open(script_path, 'w') as f:
            f.write(script)
        # Unique container name for cleanup
        cname = f"csvagent_{uuid.uuid4().hex}"
        # Docker run command
        cmd = [
            'docker', 'run', '--rm', '--name', cname,
            '--network', 'none', '--memory', '256m', '--cpus', '.5',
            '-v', f'{tmpdir}:/sandbox:ro', '-w', '/sandbox',
            'python:3.12-slim', 'python', 'script.py'
        ]
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True
            )
            return {
                'stdout': proc.stdout,
                'stderr': proc.stderr,
                'exit_code': proc.returncode,
                'timeout': False
            }
        except subprocess.TimeoutExpired as e:
            # Kill lingering container
            subprocess.run(['docker', 'kill', cname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {
                'stdout': e.stdout or '',
                'stderr': e.stderr or '',
                'exit_code': None,
                'timeout': True
            }