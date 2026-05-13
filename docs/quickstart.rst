Quick Start
===========

Installation
------------

.. code-block:: bash

   pip install sphinx-needs-svg

Or with `uv <https://docs.astral.sh/uv/>`_:

.. code-block:: bash

   uv add sphinx-needs-svg

Add to your ``conf.py``:

.. code-block:: python

   extensions = [
       "sphinx_needs",
       "sphinx_needs_svg",
   ]

Your First Diagram
------------------

Define some needs, then visualise them with ``needsvg``:

.. req:: User authentication
   :id: REQ_AUTH

   The system shall authenticate users before granting access.

.. req:: Session management
   :id: REQ_SESSION

   The system shall manage user sessions with configurable timeout.

.. spec:: OAuth2 login flow
   :id: SPEC_OAUTH
   :implements: REQ_AUTH

   Use OAuth2 authorization code flow for authentication.

Now render them as an SVG diagram with clickable links:

.. needsvg::

   <svg width="500" height="160" xmlns="http://www.w3.org/2000/svg">
     <defs>
       <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5"
               markerWidth="6" markerHeight="6" orient="auto">
         <path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>
       </marker>
     </defs>
     <a href="{{ ref('REQ_AUTH') }}">
       <rect x="10" y="10" width="150" height="50" rx="6"
             fill="#BFD8D2" stroke="#5a8a7a"/>
       <text x="85" y="30" text-anchor="middle" font-size="10"
             fill="#555">REQ_AUTH</text>
       <text x="85" y="45" text-anchor="middle" font-size="11">
         User authentication</text>
     </a>
     <a href="{{ ref('REQ_SESSION') }}">
       <rect x="10" y="90" width="150" height="50" rx="6"
             fill="#BFD8D2" stroke="#5a8a7a"/>
       <text x="85" y="110" text-anchor="middle" font-size="10"
             fill="#555">REQ_SESSION</text>
       <text x="85" y="125" text-anchor="middle" font-size="11">
         Session management</text>
     </a>
     <a href="{{ ref('SPEC_OAUTH') }}">
       <rect x="300" y="10" width="170" height="50" rx="6"
             fill="#DCB5FF" stroke="#9370DB"/>
       <text x="385" y="30" text-anchor="middle" font-size="10"
             fill="#555">SPEC_OAUTH</text>
       <text x="385" y="45" text-anchor="middle" font-size="11">
         OAuth2 login flow</text>
     </a>
     <line x1="160" y1="35" x2="300" y2="35"
           stroke="#666" stroke-width="1.5" marker-end="url(#arrow)"/>
     <text x="230" y="28" text-anchor="middle" font-size="9"
           fill="#888">implements</text>
   </svg>

The diagram above is rendered inline as SVG with clickable links back to each
need definition. Click any box to jump to that need.

Using ``flow()`` for Quick Cards
--------------------------------

For simple cases, the ``flow()`` helper renders a pre-styled card:

.. needsvg::

   <svg width="300" height="60" xmlns="http://www.w3.org/2000/svg">
     <g transform="translate(10, 5)">
       {{ flow('REQ_AUTH') }}
     </g>
     <g transform="translate(160, 5)">
       {{ flow('SPEC_OAUTH') }}
     </g>
   </svg>
