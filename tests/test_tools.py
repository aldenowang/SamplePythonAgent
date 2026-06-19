import sys
from pathlib import Path

import pytest

from cmu_project.config import AgentConfig
from cmu_project.events import EventBus
from cmu_project.tools.bash import BashTool
from cmu_project.tools.base import ToolContext
from cmu_project.tools.edit_file import EditFileTool
from cmu_project.tools.read_file import ReadFileTool
from cmu_project.tools.write_file import WriteFileTool


def make_ctx(tmp_path: Path, bash_timeout_s: int = 120) -> ToolContext:
    cfg = AgentConfig(api_key="x", bash_timeout_s=bash_timeout_s)
    return ToolContext(cfg=cfg, bus=EventBus(), confirm=None, depth=0, workdir=tmp_path)


# -- read_file -----------------------------------------------------------

def test_read_file_full(tmp_path):
    (tmp_path / "a.txt").write_text("one\ntwo\nthree", encoding="utf-8")
    res = ReadFileTool().run({"path": "a.txt"}, make_ctx(tmp_path))
    assert not res.is_error
    assert "one" in res.content and "three" in res.content


def test_read_file_slice(tmp_path):
    (tmp_path / "a.txt").write_text("l1\nl2\nl3\nl4", encoding="utf-8")
    res = ReadFileTool().run({"path": "a.txt", "offset": 2, "limit": 2}, make_ctx(tmp_path))
    assert "l2" in res.content and "l3" in res.content
    assert "l1" not in res.content and "l4" not in res.content


def test_read_file_missing(tmp_path):
    res = ReadFileTool().run({"path": "nope.txt"}, make_ctx(tmp_path))
    assert res.is_error


def test_read_file_directory(tmp_path):
    (tmp_path / "d").mkdir()
    res = ReadFileTool().run({"path": "d"}, make_ctx(tmp_path))
    assert res.is_error


# -- write_file ----------------------------------------------------------

def test_write_file_creates_dirs(tmp_path):
    res = WriteFileTool().run(
        {"path": "sub/dir/new.txt", "content": "hello"}, make_ctx(tmp_path)
    )
    assert not res.is_error
    assert (tmp_path / "sub" / "dir" / "new.txt").read_text(encoding="utf-8") == "hello"


# -- edit_file -----------------------------------------------------------

def test_edit_file_single(tmp_path):
    (tmp_path / "f.txt").write_text("alpha beta gamma", encoding="utf-8")
    res = EditFileTool().run(
        {"path": "f.txt", "old_string": "beta", "new_string": "BETA"}, make_ctx(tmp_path)
    )
    assert not res.is_error
    assert (tmp_path / "f.txt").read_text(encoding="utf-8") == "alpha BETA gamma"


def test_edit_file_replace_all(tmp_path):
    (tmp_path / "f.txt").write_text("x x x", encoding="utf-8")
    res = EditFileTool().run(
        {"path": "f.txt", "old_string": "x", "new_string": "y", "replace_all": True},
        make_ctx(tmp_path),
    )
    assert not res.is_error
    assert (tmp_path / "f.txt").read_text(encoding="utf-8") == "y y y"


def test_edit_file_not_found(tmp_path):
    (tmp_path / "f.txt").write_text("hello", encoding="utf-8")
    res = EditFileTool().run(
        {"path": "f.txt", "old_string": "zzz", "new_string": "q"}, make_ctx(tmp_path)
    )
    assert res.is_error


def test_edit_file_ambiguous(tmp_path):
    (tmp_path / "f.txt").write_text("a a", encoding="utf-8")
    res = EditFileTool().run(
        {"path": "f.txt", "old_string": "a", "new_string": "b"}, make_ctx(tmp_path)
    )
    assert res.is_error
    assert "unique" in res.content


# -- bash ----------------------------------------------------------------

def test_bash_success(tmp_path):
    res = BashTool().run({"command": "echo hello"}, make_ctx(tmp_path))
    assert not res.is_error
    assert "hello" in res.content
    assert "exit=0" in res.content


def test_bash_nonzero_exit(tmp_path):
    cmd = f'"{sys.executable}" -c "import sys; sys.exit(3)"'
    res = BashTool().run({"command": cmd}, make_ctx(tmp_path))
    assert res.is_error
    assert "exit=3" in res.content


def test_bash_timeout(tmp_path):
    cmd = f'"{sys.executable}" -c "import time; time.sleep(5)"'
    res = BashTool().run({"command": cmd}, make_ctx(tmp_path, bash_timeout_s=1))
    assert res.is_error
    assert "timed out" in res.content
