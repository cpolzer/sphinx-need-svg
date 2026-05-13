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
