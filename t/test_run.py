#!/usr/bin/env python3
"""Test utils module."""

import datetime
import sys

try:
    from run import run
    from utils import which
except ImportError:
    sys.path.append(".")
    from run import run
    from utils import which

BADPATH = "/u/jane/me/tarzan"


def test_run_test_true():
    """simple success"""
    expected = (0, "success", "", "")
    assert run(str(which("true"))) == expected


def test_run_test_false():
    """simple failure"""
    expected = (1, "calledprocesserror", "", "")
    assert run(str(which("false"))) == expected


def test_run_success():
    """successful run produces expected results"""
    today = datetime.date.today().strftime("%F\n")
    expected = (0, "success", today, "")
    assert run("date +%F") == expected


def test_run_fail():
    """unsuccessful run produces calledprocesserror"""
    observed = run(f"ls {BADPATH}")

    # TODO: this should, perhaps, be a table somewhere
    platform = sys.platform
    assert platform in {
        "darwin",
        "linux",
    }, "Platform {platform} must be 'darwin' or 'linux'"

    if platform == "darwin":
        assert observed[0] == 1
    elif platform == "linux":
        assert observed[0] == 2
    assert observed[1:3] == ("calledprocesserror", "")
    assert f"No such file or directory\n" in observed[3]


def test_run_badpath():
    """bad command produces filenotfounderror"""
    expected = (
        2,
        "filenotfounderror",
        "",
        f"[Errno 2] No such file or directory: '{BADPATH}': '{BADPATH}'",
    )
    assert run(BADPATH) == expected


def test_run_timeout():
    """timeout produces timeoutexpired"""
    expected = (124, "timeoutexpired", "", "")
    assert run("sleep 2") == expected


def test_run_no_timeout():
    """timeout produces timeoutexpired"""
    expected = (0, "success", "", "")
    assert run("sleep 2", timeout=3) == expected
