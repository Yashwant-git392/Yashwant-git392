"""Launcher safety and first-run/reuse behavior without network or a real venv."""
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location('start_project', Path(__file__).resolve().parents[1] / 'start_project.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


@pytest.fixture
def bootstrap(tmp_path, monkeypatch):
    env = tmp_path / '.venv'
    req = tmp_path / 'requirements.txt'
    req.write_text('Flask>=3\n', encoding='utf-8')
    monkeypatch.setattr(launcher, 'PROJECT', tmp_path)
    monkeypatch.setattr(launcher, 'ENV_DIR', env)
    monkeypatch.setattr(launcher, 'MARKER', env / '.shikayat-requirements.sha256')
    monkeypatch.setattr(launcher, 'REQUIREMENTS', req)
    calls = []
    def create(path, with_pip):
        assert with_pip
        py = launcher.environment_python(path)
        py.parent.mkdir(parents=True)
        py.touch()
    def fake_run(args, **kwargs):
        calls.append(args)
        if '-c' in args:
            return SimpleNamespace(returncode=0, stdout=f'{env}\n3.11\n')
        return SimpleNamespace(returncode=0, stdout='')
    monkeypatch.setattr(launcher.venv, 'create', create)
    monkeypatch.setattr(launcher, 'run', fake_run)
    monkeypatch.setattr(launcher, 'dependencies_healthy', lambda _: True)
    return env, req, calls


def test_child_environment_does_not_import_other_environments(monkeypatch):
    monkeypatch.setenv('PYTHONPATH', 'external')
    monkeypatch.setenv('PYTHONHOME', 'external')
    monkeypatch.setenv('VIRTUAL_ENV', 'external')
    monkeypatch.setenv('SHIKAYAT_DB', 'my-data.db')
    env = launcher.child_environment()
    assert all(name not in env for name in ('PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV'))
    assert env['SHIKAYAT_DB'] == 'my-data.db'
    assert os.environ['PYTHONPATH'] == 'external'


def test_first_setup_reuse_and_changed_requirements(bootstrap):
    env, req, calls = bootstrap
    python = launcher.prepare_environment()
    assert python == launcher.environment_python(env)
    assert launcher.MARKER.is_file()
    installs = lambda: sum('install' in c for c in calls)
    assert installs() == 1
    launcher.prepare_environment()
    assert installs() == 1
    req.write_text('Flask>=3\nFlask-WTF>=1\n', encoding='utf-8')
    launcher.prepare_environment()
    assert installs() == 2


def test_failed_install_does_not_mark_setup_complete(bootstrap, monkeypatch):
    _, _, calls = bootstrap
    original = launcher.run
    def fail(args, **kwargs):
        if 'install' in args:
            calls.append(args)
            return SimpleNamespace(returncode=1, stdout='')
        return original(args, **kwargs)
    monkeypatch.setattr(launcher, 'run', fail)
    with pytest.raises(RuntimeError, match='installation failed'):
        launcher.prepare_environment()
    assert not launcher.MARKER.exists()


def test_broken_existing_environment_is_not_deleted(bootstrap):
    env, _, _ = bootstrap
    env.mkdir()
    sentinel = env / 'do-not-delete.txt'
    sentinel.write_text('important', encoding='utf-8')
    with pytest.raises(RuntimeError, match='Rename .venv'):
        launcher.prepare_environment()
    assert sentinel.read_text(encoding='utf-8') == 'important'


def test_unhealthy_dependencies_are_reinstalled(bootstrap, monkeypatch):
    _, _, calls = bootstrap
    launcher.prepare_environment()
    checks = iter([False, True])
    monkeypatch.setattr(launcher, 'dependencies_healthy', lambda _: next(checks))
    launcher.prepare_environment()
    assert sum('install' in c for c in calls) == 2
