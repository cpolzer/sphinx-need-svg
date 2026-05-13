Contributing
============

Development Setup
-----------------

.. code-block:: bash

   git clone <repo-url>
   cd sphinx-needs-svg
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[test,docs]"

Running Tests
-------------

.. code-block:: bash

   # Unit + integration tests
   pytest tests/ -v

   # Build the documentation (eat-your-own-dogfood e2e)
   pytest tests/test_docs_build.py -v

   # Build docs manually
   sphinx-build -b html docs docs/_build/html

The test suite includes an **e2e test** that builds this documentation project
and verifies that ``needsvg`` directives produce working SVG output. This is
the primary dogfood test -- if the docs build, the extension works.

Project Structure
-----------------

.. code-block:: text

   sphinx-needs-svg/
   ├── src/sphinx_needs_svg/    # Extension source
   │   ├── __init__.py          # Sphinx setup()
   │   ├── directives/
   │   │   └── needsvg.py       # Directive, node, processor
   │   └── jinja_context.py     # Jinja2 context with needs helpers
   ├── tests/
   │   ├── conftest.py           # Sphinx testing fixtures
   │   ├── test_needsvg.py       # Unit/integration tests
   │   ├── test_docs_build.py    # E2E dogfood test
   │   └── roots/                # Minimal Sphinx test projects
   ├── docs/                     # Sphinx documentation (uses needsvg)
   └── pyproject.toml

Code Style
----------

- Python 3.9+
- Type hints on public APIs
- ``from __future__ import annotations`` in all modules

Testing Philosophy
------------------

Tests use Sphinx's built-in test fixtures (``sphinx.testing.fixtures``).
Each test builds a small Sphinx project and asserts on the HTML output.

The ``docs/`` directory itself is the main integration test. Every example
on every page exercises the extension. The e2e test
(``test_docs_build.py``) builds the docs with ``sphinx-build`` and checks
for SVG content in the output.

Adding Features
---------------

1. Write a failing test in ``tests/test_needsvg.py``
2. Implement the feature
3. Add an example to ``docs/examples.rst`` that exercises it
4. Run the full suite: ``pytest tests/ -v``
5. Submit a PR

Reporting Issues
----------------

Open an issue with:

- What you expected
- What happened
- Minimal RST to reproduce
- Sphinx and sphinx-needs versions
