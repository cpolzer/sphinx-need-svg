project = "sphinx-needs-svg"
copyright = "2026, sphinx-needs-svg contributors"
author = "sphinx-needs-svg contributors"

extensions = [
    "sphinx_needs",
    "sphinx_needs_svg",
]

# -- Sphinx-Needs configuration --
needs_types = [
    {"directive": "req", "title": "Requirement", "prefix": "REQ_", "color": "#BFD8D2", "style": "node"},
    {"directive": "spec", "title": "Specification", "prefix": "SPEC_", "color": "#DCB5FF", "style": "node"},
    {"directive": "impl", "title": "Implementation", "prefix": "IMPL_", "color": "#FEDCD2", "style": "node"},
    {"directive": "test", "title": "Test Case", "prefix": "TC_", "color": "#B9F6CA", "style": "node"},
]

needs_extra_links = [
    {"option": "implements", "incoming": "is implemented by", "outgoing": "implements"},
    {"option": "tests", "incoming": "is tested by", "outgoing": "tests"},
    {"option": "traces", "incoming": "is traced by", "outgoing": "traces"},
]

# -- HTML output --
html_theme = "furo"
exclude_patterns = ["_build", "superpowers"]
