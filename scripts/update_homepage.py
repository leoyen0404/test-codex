"""Update the homepage navigation with links to classified projects.

The script scans the ``projects`` directory for sub-directories that contain
``project.json`` metadata files. For each project it generates an entry in the
Classified Projects navigation section of ``index.html``.

Usage::

    python scripts/update_homepage.py

Use ``--dry-run`` to preview the generated markup without mutating files.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable, List, Sequence

DEFAULT_INDEX = Path("index.html")
DEFAULT_PROJECTS = Path("projects")
START_MARKER = "<!-- PROJECT_NAV_START -->"
END_MARKER = "<!-- PROJECT_NAV_END -->"


@dataclass
class Project:
    """Represents a classified project surfaced on the homepage."""

    name: str
    url: str
    description: str | None = None

    @property
    def nav_item(self) -> str:
        """Return the HTML snippet for this project entry."""

        title_attr = escape(self.description) if self.description else ""
        description_html = (
            f"<span class=\"description\">{escape(self.description)}</span>"
            if self.description
            else ""
        )
        title_attribute = f' title="{title_attr}"' if title_attr else ""
        return textwrap.dedent(
            f"""
            <li>
              <a href="{escape(self.url)}"{title_attribute}>{escape(self.name)}</a>
              {description_html}
            </li>
            """
        ).strip()


def discover_projects(projects_root: Path) -> List[Project]:
    """Return all projects with metadata from the provided root directory."""

    projects: List[Project] = []

    if not projects_root.exists():
        return projects

    for project_dir in sorted(projects_root.iterdir()):
        if not project_dir.is_dir():
            continue

        metadata_path = project_dir / "project.json"
        if not metadata_path.exists():
            continue

        try:
            metadata = json.loads(metadata_path.read_text())
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
            raise SystemExit(f"Invalid JSON in {metadata_path}: {exc}") from exc

        name = metadata.get("name") or project_dir.name.replace("-", " ").title()
        url = metadata.get("url") or f"{project_dir.as_posix()}/"
        description = metadata.get("description")

        projects.append(Project(name=name, url=url, description=description))

    return projects


def build_navigation_markup(projects: Sequence[Project]) -> str:
    """Create the HTML markup for the classified project navigation."""

    if not projects:
        return textwrap.dedent(
            """
            <p>No classified projects are currently published. Add a project and rerun the updater.</p>
            """
        ).strip()

    nav_items = "\n".join(
        indent_block(project.nav_item, 2) for project in projects
    )
    lines = ["<ul class=\"classified-projects\">"]
    if nav_items:
        lines.extend(nav_items.splitlines())
    lines.append("</ul>")
    return "\n".join(lines)


def indent_block(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(
        f"{pad}{line}" if line else pad for line in text.splitlines()
    )


def update_homepage(index_path: Path, markup: str) -> str:
    """Replace the placeholder markup within the index file."""

    content = index_path.read_text()
    pattern = re.compile(
        rf"(?P<indent>[ \t]*){re.escape(START_MARKER)}(.*?){re.escape(END_MARKER)}",
        flags=re.DOTALL,
    )

    match = pattern.search(content)
    if not match:
        raise SystemExit(
            "Could not find the classified project markers in the index file."
        )

    indent = match.group("indent")
    indented_markup = "\n".join(
        f"{indent}{line}" if line else line for line in markup.splitlines()
    )
    replacement = f"{indent}{START_MARKER}\n{indented_markup}\n{indent}{END_MARKER}"
    start, end = match.span()
    return f"{content[:start]}{replacement}{content[end:]}"


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--index",
        type=Path,
        default=DEFAULT_INDEX,
        help="Path to the homepage index file (default: index.html)",
    )
    parser.add_argument(
        "--projects",
        type=Path,
        default=DEFAULT_PROJECTS,
        help="Directory containing classified projects (default: projects)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Output the rendered markup instead of updating the homepage.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    projects = discover_projects(args.projects)
    markup = build_navigation_markup(projects)

    if args.dry_run:
        print(markup)
        return 0

    updated_content = update_homepage(args.index, markup)
    args.index.write_text(updated_content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
