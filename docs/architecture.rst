Architecture
============

This page documents the internal architecture of sphinx-needs-svg. It uses
``needsvg`` itself to visualise the components -- eating our own dog food.

Overview
--------

sphinx-needs-svg follows the same **two-phase rendering** pattern used by
sphinx-needs' own ``needuml`` directive:

1. **Parse phase** -- the directive runs at RST parse time, stores its content
   and options on the Sphinx environment, and emits a placeholder node.
2. **Render phase** -- a ``doctree-resolved`` event handler replaces each
   placeholder with the final inline SVG.

This split is necessary because all needs must be collected before any
``needsvg`` diagram can resolve ``ref()``, ``filter()``, or ``flow()`` calls.

Components
----------

.. spec:: Needsvg placeholder node
   :id: ARCH_NODE

   A docutils node (``nodes.General, nodes.Element``) that acts as a
   placeholder in the doctree until rendering.

.. spec:: NeedsvgDirective
   :id: ARCH_DIRECTIVE

   The RST directive registered as ``.. needsvg::``. Parses options
   (``width``, ``height``, ``align``, ``debug``), stores content on
   ``env.needsvg_all_data``, and returns a target + placeholder node.

.. spec:: process_needsvg event handler
   :id: ARCH_PROCESSOR
   :implements: ARCH_NODE

   Connected to ``doctree-resolved``. For each ``Needsvg`` node, retrieves
   stored data, renders through Jinja2, and replaces the placeholder with
   ``nodes.raw`` containing inline SVG HTML.

.. spec:: SvgJinjaContext
   :id: ARCH_JINJA

   Provides the Jinja2 template context with needs-aware helpers:
   ``needs``, ``ref()``, ``filter()``, ``flow()``.

.. spec:: render_jinja_svg function
   :id: ARCH_RENDER
   :implements: ARCH_JINJA

   Orchestrates Jinja2 rendering: creates ``SvgJinjaContext``, builds a
   ``jinja2.Environment``, compiles the template, and returns the rendered
   SVG string.

.. spec:: setup() entry point
   :id: ARCH_SETUP
   :implements: ARCH_DIRECTIVE, ARCH_NODE, ARCH_PROCESSOR

   Sphinx extension entry point. Registers the node, directive, and
   ``doctree-resolved`` event handler.

Component Diagram
~~~~~~~~~~~~~~~~~

.. needsvg::

   <svg width="680" height="280" xmlns="http://www.w3.org/2000/svg">
     <defs>
       <marker id="arch-arr" viewBox="0 0 10 10" refX="10" refY="5"
               markerWidth="6" markerHeight="6" orient="auto">
         <path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>
       </marker>
     </defs>
     <style>
       .comp rect { rx: 6; }
       .comp text { font-family: monospace; }
       .label { font-size: 9px; fill: #888; }
       .edge { stroke: #666; stroke-width: 1.5; marker-end: url(#arch-arr); }
     </style>

     <!-- setup() -->
     <a href="{{ ref('ARCH_SETUP') }}">
       <g class="comp" transform="translate(250, 5)">
         <rect width="170" height="44" fill="#e8e8e8" stroke="#999"/>
         <text x="85" y="18" text-anchor="middle" font-size="10" fill="#555">ARCH_SETUP</text>
         <text x="85" y="33" text-anchor="middle" font-size="11">setup()</text>
       </g>
     </a>

     <!-- Phase 1: Directive -->
     <text x="10" y="85" font-size="12" font-weight="bold" fill="#444">Phase 1: Parse</text>
     <a href="{{ ref('ARCH_DIRECTIVE') }}">
       <g class="comp" transform="translate(10, 95)">
         <rect width="200" height="44" fill="#DCB5FF" stroke="#9370DB"/>
         <text x="100" y="18" text-anchor="middle" font-size="10" fill="#555">ARCH_DIRECTIVE</text>
         <text x="100" y="33" text-anchor="middle" font-size="11">NeedsvgDirective</text>
       </g>
     </a>
     <a href="{{ ref('ARCH_NODE') }}">
       <g class="comp" transform="translate(250, 95)">
         <rect width="170" height="44" fill="#FEDCD2" stroke="#d4836a"/>
         <text x="85" y="18" text-anchor="middle" font-size="10" fill="#555">ARCH_NODE</text>
         <text x="85" y="33" text-anchor="middle" font-size="11">Needsvg node</text>
       </g>
     </a>
     <line class="edge" x1="210" y1="117" x2="250" y2="117"/>
     <text class="label" x="225" y="112">emits</text>

     <!-- env storage -->
     <g class="comp" transform="translate(470, 95)">
       <rect width="190" height="44" fill="#fff9c4" stroke="#f9a825"/>
       <text x="95" y="18" text-anchor="middle" font-size="10" fill="#555">env</text>
       <text x="95" y="33" text-anchor="middle" font-size="11">needsvg_all_data</text>
     </g>
     <line class="edge" x1="210" y1="127" x2="470" y2="127" stroke-dasharray="4"/>
     <text class="label" x="340" y="135">stores to</text>

     <!-- Phase 2: Render -->
     <text x="10" y="175" font-size="12" font-weight="bold" fill="#444">Phase 2: Render (doctree-resolved)</text>
     <a href="{{ ref('ARCH_PROCESSOR') }}">
       <g class="comp" transform="translate(10, 185)">
         <rect width="200" height="44" fill="#BFD8D2" stroke="#5a8a7a"/>
         <text x="100" y="18" text-anchor="middle" font-size="10" fill="#555">ARCH_PROCESSOR</text>
         <text x="100" y="33" text-anchor="middle" font-size="11">process_needsvg</text>
       </g>
     </a>
     <a href="{{ ref('ARCH_RENDER') }}">
       <g class="comp" transform="translate(250, 185)">
         <rect width="170" height="44" fill="#B9F6CA" stroke="#4CAF50"/>
         <text x="85" y="18" text-anchor="middle" font-size="10" fill="#555">ARCH_RENDER</text>
         <text x="85" y="33" text-anchor="middle" font-size="11">render_jinja_svg</text>
       </g>
     </a>
     <a href="{{ ref('ARCH_JINJA') }}">
       <g class="comp" transform="translate(470, 185)">
         <rect width="190" height="44" fill="#BBDEFB" stroke="#42A5F5"/>
         <text x="95" y="18" text-anchor="middle" font-size="10" fill="#555">ARCH_JINJA</text>
         <text x="95" y="33" text-anchor="middle" font-size="11">SvgJinjaContext</text>
       </g>
     </a>
     <line class="edge" x1="210" y1="207" x2="250" y2="207"/>
     <text class="label" x="225" y="202">calls</text>
     <line class="edge" x1="420" y1="207" x2="470" y2="207"/>
     <text class="label" x="440" y="202">uses</text>

     <!-- Output -->
     <g class="comp" transform="translate(10, 245)">
       <rect width="200" height="30" fill="#f5f5f5" stroke="#bbb"/>
       <text x="100" y="20" text-anchor="middle" font-size="11" fill="#666">nodes.raw (inline SVG)</text>
     </g>
     <line class="edge" x1="110" y1="229" x2="110" y2="245"/>

     <!-- setup arrows -->
     <line class="edge" x1="290" y1="49" x2="110" y2="95" stroke-dasharray="4"/>
     <line class="edge" x1="335" y1="49" x2="335" y2="95" stroke-dasharray="4"/>
     <line class="edge" x1="335" y1="49" x2="110" y2="185" stroke-dasharray="4"/>
     <text class="label" x="170" y="75">registers</text>
   </svg>

Data Flow
---------

1. Sphinx parses RST and encounters ``.. needsvg::``.
2. ``NeedsvgDirective.run()`` stores the raw content and options in
   ``env.needsvg_all_data[targetid]`` and returns a ``Needsvg`` placeholder.
3. After all documents are parsed, Sphinx fires ``doctree-resolved``.
4. ``process_needsvg()`` iterates each ``Needsvg`` node in the doctree.
5. For each node, it calls ``render_jinja_svg()`` which:

   a. Creates a ``SvgJinjaContext`` that loads all needs from
      ``SphinxNeedsData``.
   b. Compiles the directive body as a Jinja2 template.
   c. Renders it with ``needs``, ``ref()``, ``filter()``, ``flow()`` in
      context.

6. The rendered SVG string is wrapped in an alignment ``<div>`` and emitted
   as ``nodes.raw(..., format="html")`` -- replacing the placeholder.
7. If rendering fails, a warning is logged and an error SVG is shown instead.

File Map
--------

.. code-block:: text

   src/sphinx_needs_svg/
   ├── __init__.py              # setup() entry point
   ├── directives/
   │   ├── __init__.py
   │   └── needsvg.py           # Needsvg node, NeedsvgDirective, process_needsvg
   └── jinja_context.py         # SvgJinjaContext, render_jinja_svg
