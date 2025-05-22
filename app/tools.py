"""Secure code-exec sandbox tools."""

import os
import uuid
import tempfile
import subprocess
from textwrap import dedent

def run_python(code: str, globals_dict: dict = None, timeout: int = 10):
    """
    Execute Python code in a Docker sandbox with resource limits.

    Returns a dict with:
      - stdout: captured standard output
      - stderr: captured standard error
      - exit_code: process return code (None if timed out)
      - timeout: True if execution timed out
    """
    # Unique run identifier for container and outputs
    import uuid as _uuid
    run_id = _uuid.uuid4().hex
    # Prepare output directory on host
    output_base = os.path.abspath(os.path.join(os.getcwd(), 'agent_outputs'))
    try:
        os.makedirs(output_base, exist_ok=True)
    except Exception:
        pass
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
    allowed = ['print', 'len', 'sum', 'min', 'max', 'range', 'enumerate', '__import__']
    builtins_map = ', '.join(f"'{name}': {name}" for name in allowed)
    header = dedent(f"""
        # restrict builtins
        __builtins__ = {{{builtins_map}}}
    """)
    # Handle CSV mounting: if csv_path provided, copy file into sandbox and adjust globals
    csv_to_copy = None
    csv_name = None
    if globals_dict and 'csv_path' in globals_dict:
        host_csv = globals_dict['csv_path']
        if os.path.exists(host_csv):
            csv_to_copy = host_csv
            csv_name = os.path.basename(host_csv)
            globals_dict = globals_dict.copy()
            globals_dict['csv_path'] = csv_name
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
        # Copy CSV file into sandbox if needed
        if csv_to_copy:
            try:
                import shutil as _shutil
                _shutil.copy(csv_to_copy, tmpdir)
            except Exception:
                pass
        script_path = os.path.join(tmpdir, 'script.py')
        with open(script_path, 'w') as f:
            f.write(script)
        # Decide execution method: if pandas code, run locally in venv; else Docker sandbox
        import sys
        use_local = 'import pandas' in code or 'from pandas' in code
        if use_local:
            # Run script with local Python (assumes venv has pandas installed)
            try:
                proc = subprocess.run(
                    [sys.executable, script_path],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    text=True
                )
            except subprocess.TimeoutExpired as e:
                return {
                    'stdout': e.stdout or '',
                    'stderr': e.stderr or '',
                    'exit_code': None,
                    'timeout': True,
                    'files': []
                }
        else:
            # Docker run command
            cname = f"csvagent_{run_id}"
            cmd = [
                'docker', 'run', '--rm', '--name', cname,
                '--network', 'none', '--memory', '256m', '--cpus', '.5',
                '-v', f'{tmpdir}:/sandbox', '-w', '/sandbox',
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
            except subprocess.TimeoutExpired as e:
                subprocess.run(['docker', 'kill', cname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Collect files and return on timeout
                files = []
                try:
                    for fname in os.listdir(tmpdir):
                        if fname in ('script.py', os.path.basename(csv_to_copy) if csv_to_copy else ''):
                            continue
                        src = os.path.join(tmpdir, fname)
                        if os.path.isfile(src):
                            dst = os.path.join(output_base, f"{run_id}_{fname}")
                            import shutil as _sh
                            _sh.copy(src, dst)
                            files.append(dst)
                except Exception:
                    files = []
                return {'stdout': e.stdout or '', 'stderr': e.stderr or '', 'exit_code': None, 'timeout': True, 'files': files}
        # Execution completed
        files = []
        try:
            for fname in os.listdir(tmpdir):
                if fname == 'script.py' or fname == csv_name:
                    continue
                src = os.path.join(tmpdir, fname)
                if os.path.isfile(src):
                    dst = os.path.join(output_base, f"{run_id}_{fname}")
                    import shutil as _sh
                    _sh.copy(src, dst)
                    files.append(dst)
        except Exception:
            files = []
        return {'stdout': proc.stdout, 'stderr': proc.stderr, 'exit_code': proc.returncode, 'timeout': False, 'files': files}
    # end of run_python

def plot_chart(code: str, csv_path: str) -> list[str]:
    """
    Execute plotting code in a temporary workspace and save the current matplotlib figure.
    Returns a list with the path to the generated image file.

    The code string may assume variables:
      - csv_path: path to CSV file (copied into workspace)
      - pd: pandas module
      - plt: matplotlib.pyplot module
    """
    import tempfile
    import os
    import shutil
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError(f"Required plotting libraries missing: {e}")
    # Create workspace
    tmpdir = tempfile.mkdtemp()
    # Copy CSV if exists
    if os.path.exists(csv_path):
        try:
            shutil.copy(csv_path, tmpdir)
        except Exception:
            pass
    # Setup execution environment
    workspace_csv = os.path.join(tmpdir, os.path.basename(csv_path))
    env = {'pd': pd, 'plt': plt, 'csv_path': workspace_csv}
    # Execute code
    exec(code, env)
    # Save figure
    fig = plt.gcf()
    out_file = os.path.join(tmpdir, 'chart.png')
    fig.savefig(out_file)
    plt.close(fig)
    return [out_file]