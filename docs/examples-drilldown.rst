Drilldown Architecture
======================

This example shows how ``needsvg`` diagrams can link **directly to each
other**, creating a true **drill-down** experience.  Each SVG layer is wrapped
in an ``.. arch::`` need element with an ID.  Stage boxes use ``ref()`` to link
to the ``arch`` element of the next layer, so clicking a box jumps straight to
the detail SVG.

.. tip::

   **The pattern:**

   1. Define an ``.. arch::`` element for each SVG layer (e.g. ``ARCH_PIPELINE``,
      ``ARCH_BUILD``).
   2. Place the ``.. needsvg::`` block **inside** the ``arch`` element's content.
   3. In the SVG, link boxes to the next layer with ``ref('ARCH_BUILD')`` etc.
   4. Add a back-link in each detail SVG: ``ref('ARCH_PIPELINE')``.
   5. Add sibling links so users can jump between peer layers.

   No JavaScript, no custom code -- just sphinx-needs anchors.

Level 1 -- CI Pipeline
----------------------

.. req:: CI Pipeline
   :id: PIPE_CI

   The continuous-integration pipeline that validates every commit.

.. req:: Build stage
   :id: STAGE_BUILD
   :implements: PIPE_CI

   Compile the project and produce distributable artefacts.

.. req:: Test stage
   :id: STAGE_TEST
   :implements: PIPE_CI

   Run the full test suite against the built artefacts.

.. req:: Deploy stage
   :id: STAGE_DEPLOY
   :implements: PIPE_CI

   Publish documentation and release artefacts.

.. arch:: CI Pipeline Overview
   :id: ARCH_PIPELINE

   Top-level view of the three pipeline stages.  Click a stage to drill down.

   .. needsvg::

      <svg width="680" height="100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arr1" viewBox="0 0 10 10" refX="10" refY="5"
                  markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>
          </marker>
        </defs>
        <text x="340" y="16" text-anchor="middle" font-size="13"
              font-weight="bold" fill="#333">CI Pipeline</text>
        {% set stages = [
          {"id": "STAGE_BUILD",  "color": "#FEDCD2", "stroke": "#d4836a", "arch": "ARCH_BUILD"},
          {"id": "STAGE_TEST",   "color": "#B9F6CA", "stroke": "#4CAF50", "arch": "ARCH_TEST"},
          {"id": "STAGE_DEPLOY", "color": "#DCB5FF", "stroke": "#9370DB", "arch": "ARCH_DEPLOY"},
        ] %}
        {% for s in stages %}
          {% set x = loop.index0 * 220 + 20 %}
          <a href="{{ ref(s.arch) }}">
            <rect x="{{ x }}" y="28" width="200" height="55" rx="8"
                  fill="{{ s.color }}" stroke="{{ s.stroke }}" stroke-width="2"
                  style="cursor: pointer;"/>
            <text x="{{ x + 100 }}" y="50" text-anchor="middle"
                  font-size="10" fill="#555">{{ s.id }}</text>
            <text x="{{ x + 100 }}" y="68" text-anchor="middle"
                  font-size="12" font-weight="bold">{{ needs[s.id].title }}</text>
            <text x="{{ x + 185 }}" y="76" text-anchor="end"
                  font-size="9" fill="#999">&#x25BC; drill down</text>
          </a>
          {% if not loop.last %}
            <line x1="{{ x + 200 }}" y1="55" x2="{{ x + 220 }}" y2="55"
                  stroke="#666" stroke-width="1.5" marker-end="url(#arr1)"/>
          {% endif %}
        {% endfor %}
      </svg>

----

Level 2 -- Build Stage
----------------------

.. req:: Lint job
   :id: JOB_LINT
   :implements: STAGE_BUILD

   Run ruff linter and mypy type-checker.

.. req:: Compile job
   :id: JOB_COMPILE
   :implements: STAGE_BUILD

   Build the Python wheel with hatchling.

.. arch:: Build Stage Detail
   :id: ARCH_BUILD
   :implements: ARCH_PIPELINE

   Detail view of the Build stage.  Click Lint to drill into its steps.

   .. needsvg::

      <svg width="500" height="120" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arr2" viewBox="0 0 10 10" refX="10" refY="5"
                  markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>
          </marker>
        </defs>
        <!-- Back navigation -->
        <a href="{{ ref('ARCH_PIPELINE') }}">
          <text x="8" y="14" font-size="11" fill="#d4836a"
                style="cursor: pointer;">&#x25C0; CI Pipeline</text>
        </a>
        <!-- Breadcrumb -->
        <text x="250" y="14" text-anchor="middle" font-size="10" fill="#999">
          CI Pipeline &#x25B8; Build Stage</text>
        <text x="250" y="32" text-anchor="middle" font-size="13"
              font-weight="bold" fill="#d4836a">Build Stage</text>
        {% set jobs = [
          {"id": "JOB_LINT",    "color": "#FFF3E0", "stroke": "#E65100", "arch": "ARCH_LINT"},
          {"id": "JOB_COMPILE", "color": "#E3F2FD", "stroke": "#1565C0"},
        ] %}
        {% for j in jobs %}
          {% set x = loop.index0 * 250 + 10 %}
          {% if j.arch is defined %}
          <a href="{{ ref(j.arch) }}">
          {% else %}
          <a href="{{ ref(j.id) }}">
          {% endif %}
            <rect x="{{ x }}" y="44" width="220" height="55" rx="8"
                  fill="{{ j.color }}" stroke="{{ j.stroke }}" stroke-width="2"
                  style="cursor: pointer;"/>
            <text x="{{ x + 110 }}" y="66" text-anchor="middle"
                  font-size="10" fill="#555">{{ j.id }}</text>
            <text x="{{ x + 110 }}" y="84" text-anchor="middle"
                  font-size="12" font-weight="bold">{{ needs[j.id].title }}</text>
            {% if j.arch is defined %}
            <text x="{{ x + 205 }}" y="92" text-anchor="end"
                  font-size="9" fill="#999">&#x25BC; drill down</text>
            {% endif %}
          </a>
          {% if not loop.last %}
            <line x1="{{ x + 220 }}" y1="71" x2="{{ x + 250 }}" y2="71"
                  stroke="#666" stroke-width="1.5" marker-end="url(#arr2)"/>
          {% endif %}
        {% endfor %}
        <!-- Sibling navigation -->
        <text x="170" y="115" text-anchor="end" font-size="10" fill="#aaa">
          Stages:</text>
        <a href="{{ ref('ARCH_BUILD') }}"><text x="180" y="115" font-size="10"
           font-weight="bold" fill="#d4836a">Build</text></a>
        <a href="{{ ref('ARCH_TEST') }}"><text x="225" y="115" font-size="10"
           fill="#4CAF50">Test</text></a>
        <a href="{{ ref('ARCH_DEPLOY') }}"><text x="260" y="115" font-size="10"
           fill="#9370DB">Deploy</text></a>
      </svg>

----

Level 2 -- Test Stage
---------------------

.. req:: Unit tests job
   :id: JOB_UNIT
   :implements: STAGE_TEST

   Run pytest unit tests with coverage.

.. req:: Docs build job
   :id: JOB_DOCS
   :implements: STAGE_TEST

   Build Sphinx documentation and check for warnings.

.. arch:: Test Stage Detail
   :id: ARCH_TEST
   :implements: ARCH_PIPELINE

   Detail view of the Test stage.

   .. needsvg::

      <svg width="500" height="120" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arr3" viewBox="0 0 10 10" refX="10" refY="5"
                  markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>
          </marker>
        </defs>
        <!-- Back navigation -->
        <a href="{{ ref('ARCH_PIPELINE') }}">
          <text x="8" y="14" font-size="11" fill="#4CAF50"
                style="cursor: pointer;">&#x25C0; CI Pipeline</text>
        </a>
        <!-- Breadcrumb -->
        <text x="250" y="14" text-anchor="middle" font-size="10" fill="#999">
          CI Pipeline &#x25B8; Test Stage</text>
        <text x="250" y="32" text-anchor="middle" font-size="13"
              font-weight="bold" fill="#4CAF50">Test Stage</text>
        {% set jobs = [
          {"id": "JOB_UNIT", "color": "#E8F5E9", "stroke": "#2E7D32"},
          {"id": "JOB_DOCS", "color": "#FFF8E1", "stroke": "#F9A825"},
        ] %}
        {% for j in jobs %}
          {% set x = loop.index0 * 250 + 10 %}
          <a href="{{ ref(j.id) }}">
            <rect x="{{ x }}" y="44" width="220" height="55" rx="8"
                  fill="{{ j.color }}" stroke="{{ j.stroke }}" stroke-width="2"/>
            <text x="{{ x + 110 }}" y="66" text-anchor="middle"
                  font-size="10" fill="#555">{{ j.id }}</text>
            <text x="{{ x + 110 }}" y="84" text-anchor="middle"
                  font-size="12" font-weight="bold">{{ needs[j.id].title }}</text>
          </a>
          {% if not loop.last %}
            <line x1="{{ x + 220 }}" y1="71" x2="{{ x + 250 }}" y2="71"
                  stroke="#666" stroke-width="1.5" marker-end="url(#arr3)"/>
          {% endif %}
        {% endfor %}
        <!-- Sibling navigation -->
        <text x="170" y="115" text-anchor="end" font-size="10" fill="#aaa">
          Stages:</text>
        <a href="{{ ref('ARCH_BUILD') }}"><text x="180" y="115" font-size="10"
           fill="#d4836a">Build</text></a>
        <a href="{{ ref('ARCH_TEST') }}"><text x="225" y="115" font-size="10"
           font-weight="bold" fill="#4CAF50">Test</text></a>
        <a href="{{ ref('ARCH_DEPLOY') }}"><text x="260" y="115" font-size="10"
           fill="#9370DB">Deploy</text></a>
      </svg>

----

Level 2 -- Deploy Stage
-----------------------

.. req:: Publish docs job
   :id: JOB_PAGES
   :implements: STAGE_DEPLOY

   Deploy Sphinx docs to GitHub Pages.

.. req:: Release job
   :id: JOB_RELEASE
   :implements: STAGE_DEPLOY

   Tag and publish the Python package.

.. arch:: Deploy Stage Detail
   :id: ARCH_DEPLOY
   :implements: ARCH_PIPELINE

   Detail view of the Deploy stage.

   .. needsvg::

      <svg width="500" height="120" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arr4" viewBox="0 0 10 10" refX="10" refY="5"
                  markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>
          </marker>
        </defs>
        <!-- Back navigation -->
        <a href="{{ ref('ARCH_PIPELINE') }}">
          <text x="8" y="14" font-size="11" fill="#9370DB"
                style="cursor: pointer;">&#x25C0; CI Pipeline</text>
        </a>
        <!-- Breadcrumb -->
        <text x="250" y="14" text-anchor="middle" font-size="10" fill="#999">
          CI Pipeline &#x25B8; Deploy Stage</text>
        <text x="250" y="32" text-anchor="middle" font-size="13"
              font-weight="bold" fill="#9370DB">Deploy Stage</text>
        {% set jobs = [
          {"id": "JOB_PAGES",   "color": "#EDE7F6", "stroke": "#4527A0"},
          {"id": "JOB_RELEASE", "color": "#FCE4EC", "stroke": "#C62828"},
        ] %}
        {% for j in jobs %}
          {% set x = loop.index0 * 250 + 10 %}
          <a href="{{ ref(j.id) }}">
            <rect x="{{ x }}" y="44" width="220" height="55" rx="8"
                  fill="{{ j.color }}" stroke="{{ j.stroke }}" stroke-width="2"/>
            <text x="{{ x + 110 }}" y="66" text-anchor="middle"
                  font-size="10" fill="#555">{{ j.id }}</text>
            <text x="{{ x + 110 }}" y="84" text-anchor="middle"
                  font-size="12" font-weight="bold">{{ needs[j.id].title }}</text>
          </a>
          {% if not loop.last %}
            <line x1="{{ x + 220 }}" y1="71" x2="{{ x + 250 }}" y2="71"
                  stroke="#666" stroke-width="1.5" marker-end="url(#arr4)"/>
          {% endif %}
        {% endfor %}
        <!-- Sibling navigation -->
        <text x="170" y="115" text-anchor="end" font-size="10" fill="#aaa">
          Stages:</text>
        <a href="{{ ref('ARCH_BUILD') }}"><text x="180" y="115" font-size="10"
           fill="#d4836a">Build</text></a>
        <a href="{{ ref('ARCH_TEST') }}"><text x="225" y="115" font-size="10"
           fill="#4CAF50">Test</text></a>
        <a href="{{ ref('ARCH_DEPLOY') }}"><text x="260" y="115" font-size="10"
           font-weight="bold" fill="#9370DB">Deploy</text></a>
      </svg>

----

Level 3 -- Lint Job Steps
-------------------------

.. req:: Run ruff
   :id: STEP_RUFF
   :implements: JOB_LINT

   Execute ``ruff check`` across the source tree.

.. req:: Run mypy
   :id: STEP_MYPY
   :implements: JOB_LINT

   Execute ``mypy --strict`` on the package source.

.. arch:: Lint Job Steps Detail
   :id: ARCH_LINT
   :implements: ARCH_BUILD

   Detail view of the Lint job's individual steps.

   .. needsvg::

      <svg width="500" height="120" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <marker id="arr5" viewBox="0 0 10 10" refX="10" refY="5"
                  markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>
          </marker>
        </defs>
        <!-- Back navigation -->
        <a href="{{ ref('ARCH_BUILD') }}">
          <text x="8" y="14" font-size="11" fill="#E65100"
                style="cursor: pointer;">&#x25C0; Build Stage</text>
        </a>
        <!-- Breadcrumb -->
        <text x="250" y="14" text-anchor="middle" font-size="10" fill="#999">
          CI Pipeline &#x25B8; Build &#x25B8; Lint Job</text>
        <text x="250" y="32" text-anchor="middle" font-size="13"
              font-weight="bold" fill="#E65100">Lint Job -- Steps</text>
        {% set steps = [
          {"id": "STEP_RUFF", "color": "#FFF3E0", "stroke": "#E65100"},
          {"id": "STEP_MYPY", "color": "#FBE9E7", "stroke": "#BF360C"},
        ] %}
        {% for s in steps %}
          {% set x = loop.index0 * 250 + 10 %}
          <a href="{{ ref(s.id) }}">
            <rect x="{{ x }}" y="44" width="220" height="55" rx="8"
                  fill="{{ s.color }}" stroke="{{ s.stroke }}" stroke-width="2"/>
            <text x="{{ x + 110 }}" y="66" text-anchor="middle"
                  font-size="10" fill="#555">{{ s.id }}</text>
            <text x="{{ x + 110 }}" y="84" text-anchor="middle"
                  font-size="12" font-weight="bold">{{ needs[s.id].title }}</text>
          </a>
          {% if not loop.last %}
            <line x1="{{ x + 220 }}" y1="71" x2="{{ x + 250 }}" y2="71"
                  stroke="#666" stroke-width="1.5" marker-end="url(#arr5)"/>
          {% endif %}
        {% endfor %}
      </svg>
