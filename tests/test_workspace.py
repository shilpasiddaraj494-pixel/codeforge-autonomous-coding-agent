from pathlib import Path

import pytest

from app import workspace


def test_safe_path_rejects_escape(tmp_path, monkeypatch):
    monkeypatch.setattr(workspace.settings, "workspace_dir", tmp_path)
    with pytest.raises(ValueError):
        workspace._safe_path("../outside.txt")


def test_apply_changes_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(workspace.settings, "workspace_dir", tmp_path)

    from app.models import FileChange

    result = workspace.apply_changes([
        FileChange(
            path="hello.py",
            action="create",
            content="print('hello')\n",
            reason="test",
        )
    ])

    assert (tmp_path / "hello.py").read_text() == "print('hello')\n"
    assert result == ["created:hello.py"]


def test_command_allowlist():
    assert workspace._is_safe_command("python -m pytest")
    assert workspace._is_safe_command("python -m compileall .")
    assert not workspace._is_safe_command("rm -rf .")
    assert not workspace._is_safe_command("curl https://example.com")
