Examples
========

This page demonstrates ``needsvg`` with real sphinx-needs entities defined
right here -- eating our own dog food.

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

   <svg width="560" height="60" xmlns="http://www.w3.org/2000/svg">
     <g transform="translate(5, 5)">{{ flow('REQ_ENC') }}</g>
     <g transform="translate(140, 5)">{{ flow('SPEC_DBENC') }}</g>
     <g transform="translate(280, 5)">{{ flow('IMPL_TDE') }}</g>
     <g transform="translate(420, 5)">{{ flow('TC_ENC') }}</g>
   </svg>

Debug Mode
----------

The ``:debug:`` option shows the raw SVG source below the rendered diagram,
useful during development:

.. needsvg::
   :debug:

   <svg width="200" height="50" xmlns="http://www.w3.org/2000/svg">
     {{ flow('REQ_ENC') }}
   </svg>
