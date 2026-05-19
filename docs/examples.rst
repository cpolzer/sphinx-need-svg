Examples
========

.. toctree::
   :maxdepth: 2

   examples-drilldown

This page demonstrates ``needsvg`` with real sphinx-needs entities defined
right here -- eating our own dog food.

Drawio File Usage
-----------------

You can use `draw.io <https://www.drawio.com/>`_ to design your SVG diagrams
visually, then load them via the ``:file:`` option.  Jinja2 expressions
inside the SVG are rendered at build time, so you get clickable links to
sphinx-needs entities from a diagram you designed in a GUI.

**Drawio content sync:** When the SVG contains a drawio ``content`` attribute
(the embedded mxfile diagram data), ``needsvg`` automatically renders Jinja
expressions inside the diagram's cell labels at build time and updates the
``content`` attribute in the output.  This means the built HTML contains a
drawio SVG where both the visible SVG elements *and* the drawio diagram data
reflect the resolved sphinx-needs values.  The source ``.drawio.svg`` file is
never modified -- sync only happens in the build output.

.. important::

   **Only use simple Jinja expressions** inside drawio-exported SVGs:

   - ``{{ ref('NEED_ID') }}`` in ``<a xlink:href="...">`` attributes
   - ``{{ needs['NEED_ID'].title }}`` (or ``.id``, ``.type``, ...) inside
     ``<text>`` elements and drawio shape labels

   **Do not** use ``{{ flow('...') }}`` or ``{{ filter(...) }}`` -- these
   return SVG markup that conflicts with drawio's ``<foreignObject>`` /
   ``<switch>`` / ``<text>`` wrappers and will produce broken output.

   When editing in drawio, place the Jinja expression as the text content of
   a shape.  Then **export as SVG** (not as ``.drawio`` XML).  If drawio
   wraps your text in ``<foreignObject>``, edit the exported file to move the
   expression into a plain ``<text>`` element or an ``<a xlink:href>``
   attribute.

.. needsvg::
   :file: .media/example.drawio.svg
   :debug:

Traceability Chain
------------------

A complete requirements-to-test traceability chain:

.. req:: Data encryption at rest
   :id: REQ_ENC

   All persistent data shall be encrypted using AES-256.

.. spec:: Database-level encryption
   :id: SPEC_DBENC
   :implements: REQ_ENC

   Enable transparent data encryption (TDE) on the database engine.

.. impl:: Enable TDE on PostgreSQL
   :id: IMPL_TDE
   :implements: SPEC_DBENC

   Configure PostgreSQL with pgcrypto and TDE settings.

.. test:: Verify encrypted storage
   :id: TC_ENC
   :tests: IMPL_TDE

   Confirm data files are encrypted by inspecting raw tablespace.

.. needsvg::
   :debug:

   <svg width="680" height="80" xmlns="http://www.w3.org/2000/svg">
     <defs>
       <marker id="arr" viewBox="0 0 10 10" refX="10" refY="5"
               markerWidth="6" markerHeight="6" orient="auto">
         <path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>
       </marker>
     </defs>
     {% set items = [
       {"id": "REQ_ENC",   "color": "#BFD8D2", "stroke": "#5a8a7a"},
       {"id": "SPEC_DBENC","color": "#DCB5FF", "stroke": "#9370DB"},
       {"id": "IMPL_TDE",  "color": "#FEDCD2", "stroke": "#d4836a"},
       {"id": "TC_ENC",    "color": "#B9F6CA", "stroke": "#4CAF50"},
     ] %}
     {% for item in items %}
       {% set x = loop.index0 * 170 %}
       <a href="{{ ref(item.id) }}">
         <rect x="{{ x }}" y="10" width="150" height="50" rx="6"
               fill="{{ item.color }}" stroke="{{ item.stroke }}"/>
         <text x="{{ x + 75 }}" y="30" text-anchor="middle"
               font-size="10" fill="#555">{{ item.id }}</text>
         <text x="{{ x + 75 }}" y="45" text-anchor="middle"
               font-size="10">{{ needs[item.id].title }}</text>
       </a>
       {% if not loop.last %}
         <line x1="{{ x + 150 }}" y1="35" x2="{{ x + 170 }}" y2="35"
               stroke="#666" stroke-width="1.5" marker-end="url(#arr)"/>
       {% endif %}
     {% endfor %}
   </svg>

Dynamic Dashboard
-----------------

Automatically render all requirements using ``filter()``:

.. needsvg::
   :debug:

   <svg width="600" height="{{ (filter("type == 'req'") | length) * 55 + 10 }}"
        xmlns="http://www.w3.org/2000/svg">
     {% for need in filter("type == 'req'") %}
       {% set y = loop.index0 * 55 + 5 %}
       <a href="{{ ref(need.id) }}">
         <rect x="5" y="{{ y }}" width="580" height="45" rx="4"
               fill="#BFD8D2" stroke="#5a8a7a"/>
         <text x="15" y="{{ y + 18 }}" font-size="10"
               fill="#555" font-weight="bold">{{ need.id }}</text>
         <text x="15" y="{{ y + 34 }}" font-size="12">{{ need.title }}</text>
       </a>
     {% endfor %}
   </svg>

Flow Cards
----------

Using ``flow()`` for a compact view:

.. needsvg::
   :debug:

   <svg width="560" height="60" xmlns="http://www.w3.org/2000/svg">
     <g transform="translate(5, 5)">{{ flow('REQ_ENC') }}</g>
     <g transform="translate(140, 5)">{{ flow('SPEC_DBENC') }}</g>
     <g transform="translate(280, 5)">{{ flow('IMPL_TDE') }}</g>
     <g transform="translate(420, 5)">{{ flow('TC_ENC') }}</g>
   </svg>

Debug Mode
----------

The ``:debug:`` option shows the raw RST/Jinja source above the rendered
diagram, useful during development:

.. needsvg::
   :debug:

   <svg width="200" height="50" xmlns="http://www.w3.org/2000/svg">
     {{ flow('REQ_ENC') }}
   </svg>
