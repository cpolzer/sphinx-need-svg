project = "sphinx-need-svg"
copyright = "2026, sphinx-need-svg contributors"
author = "sphinx-need-svg contributors"

extensions = [
    "sphinx_needs",
    "sphinx_need_svg",
    "myst_parser",
]

# -- Sphinx-Needs configuration --
needs_types = [
    {"directive": "req", "title": "Requirement", "prefix": "REQ_", "color": "#BFD8D2", "style": "node"},
    {"directive": "spec", "title": "Specification", "prefix": "SPEC_", "color": "#DCB5FF", "style": "node"},
    {"directive": "impl", "title": "Implementation", "prefix": "IMPL_", "color": "#FEDCD2", "style": "node"},
    {"directive": "test", "title": "Test Case", "prefix": "TC_", "color": "#B9F6CA", "style": "node"},
    {"directive": "arch", "title": "Architecture View", "prefix": "ARCH_", "color": "#E3F2FD", "style": "node"},
]

needs_links = {
    "implements": {"incoming": "is implemented by", "outgoing": "implements"},
    "tests": {"incoming": "is tested by", "outgoing": "tests"},
    "traces": {"incoming": "is traced by", "outgoing": "traces"},
}

# -- HTML output --
html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/cpolzer/sphinx-need-svg",
    "source_branch": "main",
    "source_directory": "docs/",
}
exclude_patterns = ["_build", "superpowers"]
