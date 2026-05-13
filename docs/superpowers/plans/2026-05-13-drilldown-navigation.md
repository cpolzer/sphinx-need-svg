# Drilldown Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable SVG-to-SVG drill-down navigation in the `examples-drilldown.rst` example using `arch` need types as SVG wrappers, with back-links, breadcrumbs, and sibling navigation.

**Architecture:** Each SVG layer is wrapped in an `.. arch::` need element. Boxes link to the `arch` ID of the next layer via `ref()`. Navigation aids (back-link, breadcrumb, sibling bar) are pure SVG text elements. No code changes -- only configuration and documentation.

**Spec:** `docs/superpowers/specs/2026-05-13-drilldown-navigation-design.md`

---

## File Structure

| File | Change | Responsibility |
|---|---|---|
| `docs/conf.py` | Modify | Add `arch` need type to `needs_types` |
| `docs/examples-drilldown.rst` | Modify | Rewrite drilldown to use `arch` wrappers with navigation |

---

### Task 1: Add `arch` Need Type

**Files:**
- Modify: `docs/conf.py`

- [ ] **Step 1: Add `arch` to `needs_types`**

Add one entry to the existing `needs_types` list in `docs/conf.py`:

```python
{"directive": "arch", "title": "Architecture View", "prefix": "ARCH_",
 "color": "#E3F2FD", "style": "node"},
```

- [ ] **Step 2: Verify docs still build**

Run: `uv run sphinx-build -b html docs docs/_build/html`
Expected: Build succeeds, no warnings about unknown directive.

- [ ] **Step 3: Commit**

```bash
git add docs/conf.py
git commit -m "feat(docs): add arch need type for SVG layer navigation"
```

---

### Task 2: Wrap Level 1 SVG in `arch` Element

**Files:**
- Modify: `docs/examples-drilldown.rst`

- [ ] **Step 1: Create `ARCH_PIPELINE` element wrapping the L1 SVG**

Replace the standalone `.. needsvg::` block for the CI Pipeline with:

```rst
.. arch:: CI Pipeline Overview
   :id: ARCH_PIPELINE

   Top-level view of the three pipeline stages.  Click a stage to drill down.

   .. needsvg::

      <svg ...>
        ...
      </svg>
```

- [ ] **Step 2: Update stage box links to use `ref('ARCH_BUILD')` etc.**

Change each stage's `<a href>` from `ref(s.id)` to `ref(s.arch)` where `s.arch`
is the target `arch` element ID.  Add a `▼ drill down` hint text in the box.

- [ ] **Step 3: Verify docs build**

Run: `uv run sphinx-build -b html docs docs/_build/html`
Expected: Build succeeds, L1 SVG renders with clickable stage boxes.

---

### Task 3: Wrap Level 2 SVGs in `arch` Elements with Navigation

**Files:**
- Modify: `docs/examples-drilldown.rst`

- [ ] **Step 1: Create `ARCH_BUILD`, `ARCH_TEST`, `ARCH_DEPLOY` elements**

Each wraps its respective `.. needsvg::` block.  Each uses `:implements: ARCH_PIPELINE`.

- [ ] **Step 2: Add back-link to each L2 SVG**

Top-left of each SVG:
```xml
<a href="{{ ref('ARCH_PIPELINE') }}">
  <text x="8" y="14" font-size="11" fill="...">◀ CI Pipeline</text>
</a>
```

- [ ] **Step 3: Add breadcrumb to each L2 SVG**

Top-center:
```xml
<text x="250" y="14" text-anchor="middle" font-size="10" fill="#999">
  CI Pipeline ▸ Build Stage</text>
```

- [ ] **Step 4: Add sibling navigation to each L2 SVG**

Bottom-center, linking to all three `ARCH_*` siblings.  Current sibling is bold.

- [ ] **Step 5: In Build stage, link Lint job box to `ARCH_LINT`**

The Lint job box uses `ref('ARCH_LINT')` instead of `ref('JOB_LINT')` and shows
the drill-down hint.  Compile job (no deeper layer) keeps `ref('JOB_COMPILE')`.

- [ ] **Step 6: Increase SVG height from 100 to 120**

Extra 20px at bottom to accommodate navigation bar.

- [ ] **Step 7: Verify docs build**

Run: `uv run sphinx-build -b html docs docs/_build/html`
Expected: All three L2 SVGs render with back-link, breadcrumb, and sibling nav.

---

### Task 4: Wrap Level 3 SVG in `arch` Element with Navigation

**Files:**
- Modify: `docs/examples-drilldown.rst`

- [ ] **Step 1: Create `ARCH_LINT` element wrapping the L3 SVG**

Uses `:implements: ARCH_BUILD`.

- [ ] **Step 2: Add back-link to Build Stage**

```xml
<a href="{{ ref('ARCH_BUILD') }}">
  <text ...>◀ Build Stage</text>
</a>
```

- [ ] **Step 3: Add breadcrumb**

```xml
CI Pipeline ▸ Build ▸ Lint Job
```

- [ ] **Step 4: Verify docs build**

Run: `uv run sphinx-build -b html docs docs/_build/html`
Expected: L3 SVG renders with back-link and breadcrumb.

---

### Task 5: Update Page Introduction and Tips

**Files:**
- Modify: `docs/examples-drilldown.rst`

- [ ] **Step 1: Rewrite intro to explain the `arch` wrapper pattern**

Describe: each SVG layer is an `arch` element; boxes link to arch IDs; back-links
and sibling nav aid traversal.

- [ ] **Step 2: Update the tip box**

Replace the old tip about `ref()` + need placement with the new pattern
explanation.

---

### Task 6: Final Build Verification

- [ ] **Step 1: Clean build**

Run: `uv run sphinx-build -E -b html docs docs/_build/html`
Expected: Build succeeds with 0 warnings.

- [ ] **Step 2: Manually verify navigation in browser**

Open `docs/_build/html/examples-drilldown.html`:
1. Click "Build stage" box in L1 -> scrolls to `ARCH_BUILD` SVG
2. Click "◀ CI Pipeline" in L2 Build -> scrolls back to `ARCH_PIPELINE`
3. Click "Test" in sibling nav -> scrolls to `ARCH_TEST`
4. Click "Lint job" in Build -> scrolls to `ARCH_LINT`
5. Click "◀ Build Stage" in L3 -> scrolls back to `ARCH_BUILD`

- [ ] **Step 3: Commit**

```bash
git add docs/
git commit -m "feat(docs): drilldown navigation using arch need wrappers"
```
