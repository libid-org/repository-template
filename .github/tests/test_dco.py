"""Exercise the actual DCO workflow shell; optionally pass other workflow paths."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap


def git(*args, **kwargs):
    return subprocess.check_output(["git", *args], text=True, **kwargs).strip()


paths = [Path(p).resolve() for p in sys.argv[1:]] or [
    Path(__file__).resolve().parents[1] / "workflows/dco.yml"
]
bot = "dependabot[bot]"
bot_email = "49699333+dependabot[bot]@users.noreply.github.com"
support = f"{bot} <support@github.com>"
cases = [
    ("Contributor", "contributor@example.com", "Contributor <contributor@example.com>", True),
    ("Contributor", "contributor@example.com", "Someone else <else@example.com>", False),
    ("Contributor", "contributor@example.com", "", False),
    (bot, bot_email, support, True),
    (bot, bot_email, f"{bot} <{bot_email}>", True),
    (bot, bot_email, "", False),
    (bot, bot_email, "Someone else <else@example.com>", False),
    ("Contributor", "contributor@example.com", support, False),
    (bot, "impostor@example.com", support, False),
]

with tempfile.TemporaryDirectory(prefix="dco-test-") as directory:
    git("init", "-q", directory)
    for path in paths:
        blocks = re.findall(r"(?m)^        run: \|\n((?:          .*\n|\n)+)", path.read_text())
        scripts = [textwrap.dedent(b) for b in blocks if 'author=$(git log' in b]
        assert len(scripts) == 1, f"Expected one author-checking DCO step in {path}"
        for name, email, trailer, expected in cases:
            env = dict(os.environ, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email,
                       GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=email)
            message = "chore: test DCO\n\n" + (f"Signed-off-by: {trailer}\n" if trailer else "")
            git("-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                "commit", "--allow-empty", "-q", "-m", message, cwd=directory, env=env)
            sha = git("rev-parse", "HEAD", cwd=directory)
            env.update(EVENT_NAME="push", PUSH_BEFORE="0" * 40, PUSH_AFTER=sha,
                       BASE_SHA="", HEAD_SHA="")
            result = subprocess.run(["bash", "-c", scripts[0]], cwd=directory,
                                    env=env, capture_output=True, text=True)
            assert (result.returncode == 0) == expected, (
                path, name, email, trailer, result.stdout, result.stderr
            )
        print(f"PASS: {path} ({len(cases)} DCO cases)")
