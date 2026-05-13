# sphinx-need-svg

A [Sphinx-Needs](https://sphinx-needs.readthedocs.io/) extension for rendering
SVG diagrams with clickable links to needs entities.

Write SVG markup with Jinja2 templating directly in your RST documentation.

## Quick Start

```bash
pip install sphinx-need-svg
```

Add to `conf.py`:

```python
extensions = ["sphinx_needs", "sphinx_need_svg"]
```

Use in RST:

```rst
.. needsvg::

   <svg width="200" height="50">
     <a href="{{ ref('REQ_001') }}">
       <text x="10" y="30">{{ needs['REQ_001'].title }}</text>
     </a>
   </svg>
```

## Development

```bash
mise install     # set up Python via mise
mise run install # install deps with uv
mise run test    # run tests
mise run docs    # build documentation
```

See the [documentation](docs/) for full details.
