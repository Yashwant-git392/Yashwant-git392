"""Create a local virtual environment on first use, then run the demo.

This bootstrap uses the Python standard library only. It never deletes an
existing environment or database. On later runs it reuses a healthy setup.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import venv

PROJECT = Path(__file__).resolve().parent
ENV_DIR = PROJECT / '.venv'
REQUIREMENTS = PROJECT / 'requirements.txt'
MARKER = ENV_DIR / '.shikayat-requirements.sha256'
MIN_PYTHON = (3, 10)


def environment_python(env_dir: Path | None = None) -> Path:
    env_dir = env_dir or ENV_DIR
    if os.name == 'nt':
        return env_dir / 'Scripts' / 'python.exe'
    return env_dir / 'bin' / 'python'


def child_environment() -> dict[str, str]:
    # Do not accidentally import packages from the shell's external environment.
    env = os.environ.copy()
    env.pop('PYTHONHOME', None)
    env.pop('PYTHONPATH', None)
    env.pop('VIRTUAL_ENV', None)
    return env


def run(args, **kwargs):
    return subprocess.run(args, cwd=PROJECT, env=child_environment(), **kwargs)


def dependencies_healthy(python: Path) -> bool:
    imports = run([str(python), '-c', 'import flask, flask_wtf, pytest'],
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if imports.returncode:
        return False
    check = run([str(python), '-m', 'pip', 'check'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return check.returncode == 0


def prepare_environment() -> Path:
    if sys.version_info < MIN_PYTHON:
        raise RuntimeError('Python 3.10 or newer is required. Install Python 3.11 or 3.12 and try again.')
    python = environment_python()
    if not ENV_DIR.exists():
        print('First run: creating a virtual environment in .venv ...', flush=True)
        try:
            venv.create(ENV_DIR, with_pip=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError('Could not create .venv. Check your Python installation; on Debian/Ubuntu, '
                               'install the matching python3-venv package. If .venv was partially created, '
                               'rename it and retry.') from exc
    if not python.is_file():
        raise RuntimeError('The existing .venv does not contain its Python interpreter. '
                           'It may be broken or from another computer. Rename .venv and start again; '
                           'do not delete your database.')
    try:
        probe = run([str(python), '-c',
                     'import sys; print(sys.prefix); print("%s.%s" % sys.version_info[:2])'],
                    capture_output=True, text=True)
    except OSError as exc:
        raise RuntimeError('Cannot run the existing .venv Python. Rename .venv and start again.') from exc
    lines = probe.stdout.splitlines()
    if probe.returncode or len(lines) < 2 or Path(lines[0]).resolve() != ENV_DIR.resolve():
        raise RuntimeError('The existing .venv is not usable in this folder. '
                           'Rename .venv and start again; your database will not be touched.')
    if tuple(map(int, lines[1].split('.'))) < MIN_PYTHON:
        raise RuntimeError('The existing .venv uses an old Python. Rename .venv and use Python 3.10 or newer.')
    fingerprint = hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()
    try:
        installed = MARKER.read_text(encoding='ascii').strip() == fingerprint
    except (FileNotFoundError, OSError, UnicodeError):
        installed = False
    if not installed or not dependencies_healthy(python):
        print('Installing or repairing project dependencies (internet may be needed) ...', flush=True)
        result = run([str(python), '-m', 'pip', 'install', '-r', str(REQUIREMENTS)])
        if result.returncode:
            raise RuntimeError('Dependency installation failed. Check your internet connection and pip output, then retry. '
                               'If the environment is broken, rename .venv and start again.')
        if not dependencies_healthy(python):
            raise RuntimeError('Dependencies could not be verified. Review the pip output, rename .venv and retry.')
        MARKER.write_text(fingerprint + '\n', encoding='ascii')
    else:
        print('Using the existing project virtual environment.', flush=True)
    return python


def main() -> int:
    try:
        python = prepare_environment()
        print('Starting Campus Shikayat Setu. Open http://127.0.0.1:' +
              os.environ.get('SHIKAYAT_PORT', '5001') + ' in your browser. Press Ctrl+C to stop.', flush=True)
        return run([str(python), str(PROJECT / 'run.py')]).returncode
    except KeyboardInterrupt:
        print('\nStopped.')
        return 0
    except (RuntimeError, OSError) as exc:
        print(f'Unable to start: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
