Test
====

.. req:: My Requirement
   :id: REQ_001

   A test requirement.

.. needsvg::

   <svg width="200" height="50">
     <rect width="200" height="50" fill="#eef"/>
   </svg>

.. needsvg::

   <svg width="300" height="50">
     <a href="{{ ref('REQ_001') }}">
       <text x="10" y="30">{{ needs['REQ_001'].title }}</text>
     </a>
   </svg>

.. req:: Second Requirement
   :id: REQ_002

   Another requirement.

.. needsvg::

   <svg width="400" height="50">
     {% for need in filter("type == 'req'") %}
       <text x="{{ loop.index0 * 150 }}" y="30">{{ need.title }}</text>
     {% endfor %}
   </svg>

.. needsvg::
   :debug:
   :width: 300
   :height: 80

   <svg>
     <rect width="100" height="40" fill="#ccc"/>
   </svg>

.. needsvg::

   <svg width="200" height="60">
     {{ flow('REQ_001') }}
   </svg>
