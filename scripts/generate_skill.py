#!/usr/bin/env python3
"""Generate SKILL.md from source code via AST introspection and Jinja2 templating."""

from __future__ import annotations

import argparse
import ast
import sys
import warnings
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src" / "sphinx_need_svg"


def extract_version() -> str:
    """Extract version from __init__.py setup() return dict."""
    source = (SRC / "__init__.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "setup":
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Dict):
                    for key, value in zip(stmt.value.keys, stmt.value.values):
                        if (
                            isinstance(key, ast.Constant)
                            and key.value == "version"
                            and isinstance(value, ast.Constant)
                        ):
                            return str(value.value)
    raise RuntimeError("Could not extract version from __init__.py")


def extract_directive_options() -> list[str]:
    """Extract option names from NeedsvgDirective.option_spec via AST."""
    source = (SRC / "directives" / "needsvg.py").read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == "NeedsvgDirective"):
            continue
        for item in node.body:
            value = None
            if (
                isinstance(item, ast.AnnAssign)
                and isinstance(item.target, ast.Name)
                and item.target.id == "option_spec"
            ):
                value = item.value
            elif isinstance(item, ast.Assign):
                for t in item.targets:
                    if isinstance(t, ast.Name) and t.id == "option_spec":
                        value = item.value
                        break
            if value is not None and isinstance(value, ast.Dict):
                return [str(k.value) for k in value.keys if isinstance(k, ast.Constant)]
    raise RuntimeError("Could not find option_spec in NeedsvgDirective")


def extract_jinja_helpers() -> list[dict[str, str | bool]]:
    """Extract public methods and properties from SvgJinjaContext via AST."""
    source = (SRC / "jinja_context.py").read_text()
    tree = ast.parse(source)

    helpers: list[dict[str, str | bool]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == "SvgJinjaContext"):
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            name = item.name
            if name.startswith("_") or name == "get_context":
                continue

            docstring = ast.get_docstring(item) or ""
            is_property = any(
                isinstance(dec, ast.Name) and dec.id == "property"
                for dec in item.decorator_list
            )

            if is_property:
                helpers.append(
                    {
                        "name": name,
                        "signature": name,
                        "docstring": docstring,
                        "is_property": True,
                    }
                )
            else:
                args = [a.arg for a in item.args.args if a.arg != "self"]
                helpers.append(
                    {
                        "name": name,
                        "signature": f"{name}({', '.join(args)})",
                        "docstring": docstring,
                        "is_property": False,
                    }
                )

    if not helpers:
        warnings.warn(
            "No Jinja helpers found in SvgJinjaContext. Was the class renamed?",
            stacklevel=1,
        )
    return helpers


def extract_needs_types() -> list[dict[str, str]]:
    """Extract needs_types from docs/conf.py using ast.literal_eval."""
    conf_path = REPO_ROOT / "docs" / "conf.py"
    if not conf_path.exists():
        return []

    source = conf_path.read_text()

    # Find the needs_types = [...] block and parse it as a Python literal
    # Use AST to find the assignment reliably
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "needs_types" for t in node.targets
        ):
            # Extract the source text for this node and eval it
            try:
                raw = ast.literal_eval(node.value)
                return [
                    {
                        "directive": t.get("directive", ""),
                        "title": t.get("title", ""),
                        "prefix": t.get("prefix", ""),
                        "color": t.get("color", ""),
                    }
                    for t in raw
                ]
            except (ValueError, TypeError) as e:
                warnings.warn(f"Could not parse needs_types: {e}", stacklevel=1)
                return []
    return []


def extract_needs_links() -> dict[str, dict[str, str]]:
    """Extract needs_links from docs/conf.py using ast.literal_eval."""
    conf_path = REPO_ROOT / "docs" / "conf.py"
    if not conf_path.exists():
        return {}

    source = conf_path.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "needs_links" for t in node.targets
        ):
            try:
                return ast.literal_eval(node.value)
            except (ValueError, TypeError) as e:
                warnings.warn(f"Could not parse needs_links: {e}", stacklevel=1)
                return {}
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SKILL.md")
    parser.add_argument(
        "-o",
        "--output",
        default=str(REPO_ROOT / "SKILL.md"),
        help="Output file path (default: SKILL.md at repo root)",
    )
    args = parser.parse_args()

    try:
        version = extract_version()
        option_names = extract_directive_options()
        helpers = extract_jinja_helpers()
        needs_types = extract_needs_types()
        needs_links = extract_needs_links()

        if not option_names:
            raise RuntimeError("No directive options extracted -- check needsvg.py")
        if not helpers:
            raise RuntimeError("No Jinja helpers extracted -- check jinja_context.py")

        context = {
            "version": version,
            "option_names": option_names,
            "helpers": helpers,
            "needs_types": needs_types,
            "needs_links": needs_links,
        }

        env = Environment(
            loader=FileSystemLoader(str(REPO_ROOT / "scripts")),
            keep_trailing_newline=True,
        )
        template = env.get_template("skill_template.md.j2")
        output = template.render(**context)

        Path(args.output).write_text(output)
        print(f"Generated: {args.output}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
