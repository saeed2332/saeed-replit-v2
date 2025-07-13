"""
saeed_replit – tiny workspace-scaffolding helper.

At the moment it only exposes `init_project(dest)`, just enough to
satisfy the test-suite in tests/test_workspace_init.py.  Evolve it as
your agent learns new tricks.
"""
from pathlib import Path
import shutil
import textwrap


TEMPLATE_README = textwrap.dedent(
    """\
    # New Auto-Gen Project

    Congratulations – your workspace has been scaffolded!
    """
)

def init_project(dest: str | Path) -> Path:
    """
    Create a minimal project skeleton under *dest* and return the path.

    Parameters
    ----------
    dest : str | pathlib.Path
        Destination directory (created if needed).

    Returns
    -------
    pathlib.Path
        Path object pointing to the created project root.
    """
    dest = Path(dest).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)

    # example scaffold: README plus empty src/ directory
    (dest / "README.md").write_text(TEMPLATE_README, encoding="utf-8")
    (dest / "src").mkdir(exist_ok=True)

    return dest
