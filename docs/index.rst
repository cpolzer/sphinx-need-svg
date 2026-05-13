sphinx-needs-svg
=================

A Sphinx-Needs extension for rendering SVG diagrams with clickable links to
needs entities.

Write SVG markup with Jinja2 templating directly in your RST documentation.
Jinja helpers like ``ref()``, ``filter()``, and ``flow()`` give you access to
sphinx-needs data at build time.

.. code-block:: rst

   .. needsvg::

      <svg width="400" height="60">
        {% for need in filter("type == 'req'") %}
          <a href="{{ ref(need.id) }}">
            <rect x="{{ loop.index0 * 130 }}" y="5" width="120" height="40"
                  rx="4" fill="#ddeeff" stroke="#336699"/>
            <text x="{{ loop.index0 * 130 + 60 }}" y="30"
                  text-anchor="middle" font-size="11">{{ need.title }}</text>
          </a>
        {% endfor %}
      </svg>

.. toctree::
   :maxdepth: 2
   :caption: Contents

   quickstart
   reference
   examples
   architecture
   contributing
