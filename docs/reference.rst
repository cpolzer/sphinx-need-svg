Directive Reference
===================

``needsvg`` Directive
---------------------

Renders SVG markup with Jinja2 templating and sphinx-needs integration.

.. code-block:: rst

   .. needsvg::
      :width: 400
      :height: 100
      :align: center
      :debug:

      <svg>
        ...Jinja2-templated SVG content...
      </svg>

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 10 15 60

   * - Option
     - Type
     - Default
     - Description
   * - ``:width:``
     - string
     - ``100%``
     - SVG container width
   * - ``:height:``
     - string
     - ``auto``
     - SVG container height
   * - ``:align:``
     - choice
     - ``center``
     - Horizontal alignment: ``left``, ``center``, or ``right``
   * - ``:debug:``
     - flag
     -
     - Show the raw SVG source as a code block below the rendered diagram

Jinja2 Helpers
--------------

The following helpers are available in the directive body:

``needs``
~~~~~~~~~

A dictionary of all sphinx-needs entities, keyed by ID.

.. code-block:: jinja

   {{ needs['REQ_001'].title }}
   {{ needs['REQ_001'].type }}
   {{ needs['REQ_001'].docname }}

``ref(need_id)``
~~~~~~~~~~~~~~~~

Returns the URL to a need's anchor in the documentation. Use inside SVG
``<a>`` elements:

.. code-block:: jinja

   <a href="{{ ref('REQ_001') }}">
     <text>Click me</text>
   </a>

Returns ``#UNKNOWN-<id>`` if the need does not exist.

``filter(expression)``
~~~~~~~~~~~~~~~~~~~~~~

Returns a list of needs matching a filter expression. Uses the same filter
syntax as sphinx-needs:

.. code-block:: jinja

   {% for need in filter("type == 'req'") %}
     <text>{{ need.title }}</text>
   {% endfor %}

``flow(need_id)``
~~~~~~~~~~~~~~~~~

Returns a pre-styled SVG ``<g>`` element (a card with ID and title) wrapped
in a clickable ``<a>`` link. Useful for quick diagrams without hand-crafting
SVG:

.. code-block:: jinja

   <svg width="200" height="60">
     {{ flow('REQ_001') }}
   </svg>

The card is 120x40 pixels with rounded corners, a light blue fill, and the
need's ID and title as text.

Error Handling
--------------

If a Jinja2 template error occurs (e.g. referencing a nonexistent need with
bracket notation), the build does **not** crash. Instead:

- A warning is logged with the source file and line number
- The SVG is replaced with a red error message

.. code-block:: rst

   .. needsvg::

      <svg>{{ needs['NONEXISTENT'].title }}</svg>

This renders as: ``needsvg error: 'NONEXISTENT'``
