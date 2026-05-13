Contributing
============

Prerequisites
-------------

- `mise <https://mise.jdx.dev/>`_ -- manages Python version and task runner
- `uv <https://docs.astral.sh/uv/>`_ -- fast Python package manager

Development Setup
-----------------

.. code-block:: bash

   git clone <repo-url>
   cd sphinx-need-svg
   mise install          # installs Python 3.12
   uv sync --all-extras  # creates .venv, installs all deps

This gives you a working environment with the extension installed in editable
mode plus all test, docs, and dev dependencies (ruff, mypy).

Available Tasks
---------------

All tasks are defined in ``.mise.toml`` and run via ``mise run <task>``:

.. list-table::
   :header-rows: 1
   :widths: 20 50

   * - Task
     - Description
   * - ``mise run test``
     - Run full test suite (unit + e2e)
   * - ``mise run test-unit``
     - Run unit/integration tests only
   * - ``mise run test-e2e``
     - Run e2e docs build test
   * - ``mise run lint``
     - Run ruff linter
   * - ``mise run lint-fix``
     - Run ruff linter with auto-fix
   * - ``mise run format``
     - Format code with ruff
   * - ``mise run format-check``
     - Check formatting without modifying
   * - ``mise run typecheck``
     - Run mypy type checker
   * - ``mise run check``
     - Run all checks (lint + format + mypy + test)
   * - ``mise run docs``
     - Build HTML documentation
   * - ``mise run docs-clean``
     - Clean and rebuild documentation
   * - ``mise run build``
     - Build sdist and wheel with uv
   * - ``mise run clean``
     - Remove build artifacts

Before submitting a PR, run the full check suite:

.. code-block:: bash

   mise run check

This runs ruff lint, ruff format check, mypy, and pytest in sequence.

Running Tests
-------------

.. code-block:: bash

   mise run test          # all tests
   mise run test-unit     # unit/integration tests only
   mise run test-e2e      # e2e docs build test only

The test suite includes an **e2e dogfood test** that builds this documentation
project and verifies that ``needsvg`` directives produce working SVG output.
If the docs build and the SVG assertions pass, the extension works.

Building Documentation
----------------------

.. code-block:: bash

   mise run docs          # build to docs/_build/html
   mise run docs-clean    # clean + rebuild

Open ``docs/_build/html/index.html`` in a browser to review.

Packaging
---------

.. code-block:: bash

   mise run build         # produces dist/*.tar.gz and dist/*.whl

Uses `hatchling <https://hatch.pypa.io/>`_ as the build backend and
`uv build <https://docs.astral.sh/uv/>`_ as the build frontend.

Project Structure
-----------------

.. code-block:: text

   sphinx-need-svg/
   ├── .mise.toml               # mise tasks and Python version
   ├── pyproject.toml            # package metadata, deps, tool config
   ├── uv.lock                   # reproducible dependency lock
   ├── LICENSE                   # MIT license
   ├── README.md
   ├── SKILL.md                  # generated AI agent skill (do not edit)
   ├── scripts/
   │   ├── generate_skill.py     # AST-based SKILL.md generator
   │   └── skill_template.md.j2  # Jinja2 template for SKILL.md
   ├── src/sphinx_need_svg/     # extension source
   │   ├── __init__.py           # Sphinx setup()
   │   ├── directives/
   │   │   └── needsvg.py        # directive, node, processor
   │   └── jinja_context.py      # Jinja2 context with needs helpers
   ├── tests/
   │   ├── conftest.py           # Sphinx testing fixtures
   │   ├── test_needsvg.py       # unit/integration tests
   │   ├── test_docs_build.py    # e2e dogfood test
   │   └── roots/                # minimal Sphinx test projects
   └── docs/                     # Sphinx docs (uses needsvg itself)

Code Quality
------------

**Linting** -- `ruff <https://docs.astral.sh/ruff/>`_ with rules: ``E``,
``F``, ``I``, ``UP``, ``B``, ``SIM``, ``RUF``.

**Formatting** -- ruff format (black-compatible).

**Type checking** -- `mypy <https://mypy-lang.org/>`_ in strict mode.
``docutils`` and ``sphinx_needs`` imports have stubs ignored since those
libraries don't ship type annotations.

**Style conventions:**

- Python 3.9+ compatible syntax
- Type hints on all public APIs
- ``from __future__ import annotations`` in all modules

Testing Philosophy
------------------

Tests use Sphinx's built-in test fixtures (``sphinx.testing.fixtures``).
Each test builds a small Sphinx project and asserts on the HTML output.

The ``docs/`` directory itself is the main integration test. Every example
on every page exercises the extension. The e2e test
(``test_docs_build.py``) builds the docs and checks for SVG content
in the output.

AI Agent Skill (``SKILL.md``)
-----------------------------

The repository includes a generated ``SKILL.md`` at the project root.
This file teaches AI coding agents (Claude Code, OpenCode, Copilot, etc.)
how to use ``sphinx-need-svg`` — directive options, Jinja helpers,
configuration, and common patterns like drilldown navigation.

**Regenerating the skill file:**

.. code-block:: bash

   uv run python scripts/generate_skill.py

The generator uses AST-based extraction to pull directive options, Jinja
helpers, ``needs_types``, and ``needs_links`` from the source code and
``docs/conf.py``.  Static prose (patterns, common mistakes) lives in the
Jinja2 template at ``scripts/skill_template.md.j2``.

The output is deterministic — running the generator twice produces the
same ``SKILL.md``.  CI automatically regenerates and commits the file on
pushes to ``main`` (the ``update-skill`` job in ``.github/workflows/ci.yml``).

When to regenerate manually:

- After adding or renaming directive options in ``needsvg.py``
- After adding or changing Jinja helpers in ``jinja_context.py``
- After modifying ``needs_types`` or ``needs_links`` in ``docs/conf.py``
- After updating the template prose in ``scripts/skill_template.md.j2``

Adding Features
---------------

1. Write a failing test in ``tests/test_needsvg.py``
2. Implement the feature
3. Add an example to ``docs/examples.rst`` that exercises it
4. Run ``mise run check`` to verify everything passes
5. Regenerate ``SKILL.md`` if the change affects the public API (see above)
6. Submit a PR

Reporting Issues
----------------

Open an issue with:

- What you expected
- What happened
- Minimal RST to reproduce
- Sphinx and sphinx-needs versions (``pip list | grep sphinx``)
