---
name: origami-solving-pipeline
description: End-to-end guide for running the automated box-pleating origami pipeline with `bp_pipeline` (`bp`). Covers stick-figure normalization (`bp.prepare`), integer-grid packing (`bp.pack`, `bp.stack`), flat-foldable MV hinge solving (`bp.solve`, `bp.solve_best`, `bp.solve_sweep`, `bp.fold`), 3D geometric shaping (`bp.shape`), exporting to Box Pleating Studio (`.bps.json`), `.svg`, and `.fold`, and interactive web inspection. Use when orchestrating or debugging any stage of the box-pleating solver pipeline.
---

# End-to-End Box-Pleating Origami Solving Pipeline (`bp_pipeline`)

`bp_pipeline` (`bp`) is an end-to-end automated design, packing,
flat-foldable Mountain/Valley (MV) assignment, and 3D shaping pipeline for
box-pleated origami.

--------------------------------------------------------------------------------

## 1. Pipeline Architecture & Immutable Data Bus

Every stage of `bp_pipeline` consumes and produces an immutable,
JSON-serializable bus record (`bp_pipeline.bus`):

```
StickFigure / JSON / Example Name
        │
        ▼  bp.prepare(...)
   DesignTree                 (source + merged StickFigure, symmetry, bounds)
        │
        ▼  bp.pack(...)  or  bp.stack(...)
PackedCreasePattern           (integer grid_size, Flaps, Rivers, Hinges)
        │
        ▼  bp.solve_best(...)  or  bp.solve_sweep(...)
SolvedCreasePattern           (flat-foldable MV CreasePattern, SolveStats)
        │
        ├──► bp.to_svg(...)        ──► .svg  (Mountain=red, Valley=blue)
        ├──► bp.to_fold(...)       ──► .fold (FOLD v1.2 JSON)
        ├──► bp.to_bp_studio(...)  ──► .bps.json (BoxPleatingTreeData schema)
        │
        ▼  bp.shape(...)
  ShapedCreasePattern         (3D geometric simple folds, river bends)
        │
        ├──► shaped.to_svg()                 ──► .svg  (Shaped CP with partial fold opacity)
        ├──► bp.to_fold(shaped)              ──► .fold (Shaped FOLD v1.2 JSON)
        └──► shaped.flat_fold(strict=False)  ──► FOLD dict (2D folded state)
```

--------------------------------------------------------------------------------

## 2. Quickstart: One-Call vs. Stage-by-Stage Execution

### Option A: One-Call End-to-End Pipeline (`bp.fold`)

```python
import bp_pipeline as bp

# Accepts an example name ('human', 'scorpion', 'cat', 'spider'),
# a StickFigure object, a dict, or a JSON string:
result = bp.fold('human', preset='demo')

print(f'Grid size: {result.packed.grid_size}x{result.packed.grid_size}')
print(f'Globally flat-foldable: {result.solved.is_globally_flat_foldable}')

# Render SVG crease pattern string:
svg_str = result.solved.to_svg()
```

Available presets for `bp.fold(..., preset=...)`:

-   `'demo'`: Fast interactive preset ($\le 15\text{s}$ packing, $1500$ solver
    steps, stops on first valid solution).
-   `'fast'`: Medium budget ($\le 30\text{s}$ packing, $3000$ solver steps
    across guided & unguided sweeps, stops on first valid solution).
-   `'production'`: Full SOTA sweep across extra grid sizes and all 6
    `PRODUCTION_SWEEP` solver configurations, collecting and ranking all
    flat-foldable candidates.

### Option B: Stage-by-Stage Pipeline Control

```python
import bp_pipeline as bp

# 1. Normalize input into a DesignTree:
design = bp.prepare('human')

# 2. Pack flaps and rivers onto an integer square grid:
packed = bp.pack(design)

# 3. Solve for the highest-scoring globally flat-foldable MV assignment:
solved = bp.solve_best(packed)

# 4. Or run a solver sweep across multiple SolverConfigs:
candidates = bp.solve_sweep(packed, configs=bp.PRODUCTION_SWEEP[:1])

# 5. Apply 3D geometric shaping from the unmerged StickFigure:
shaped = bp.shape(solved)
```

--------------------------------------------------------------------------------

## 3. Stage Details & SOTA Configurations

### Stage 1: Design Preparation (`bp.prepare`)

-   Merges degree-2 linear flap chains via `source.merge_linear_chains()` into
    `design.merged`, recording provenance in `design.merged_from`.
-   Computes bilateral symmetry partnerships (`design.symmetric_partner`,
    `design.is_symmetric`) and theoretical grid bounds (`design.min_grid_size`,
    `design.max_grid_size`).

### Stage 2: Integer-Grid Packing (`bp.pack` & `bp.stack`)

-   **`bp.pack(design, config=PackingTaskConfig(...))`**:
    -   Searches over integer grid sizes $G = G_{\min} + \Delta G$ (enforcing
        even $G$ when `design.is_symmetric` is `True`).
    -   Places straight, L-shaped, and hugging rivers
        (`include_straight_rivers=True`, `include_lshape_rivers=True`,
        `use_l_shaped_level_shifter=True`) and tiles flap rectangles via
        backtracking search (`traversal_mode='river_priority'`).
    -   Automatically runs a Pass-1 packing budget (`55%` of the outer timeout
        with `star_hub_rivers=True`), followed by a Pass-2 recovery sweep when
        Pass 1 yields no packing (including on timeout) that enables all 4
        recovery flags: `star_hub_rivers=True`, `symmetry_line_obstacles=True`,
        `prune_partial_border_overhang=True`, and
        `stretch_intermediate_pocket_flaps=True`.
    -   For bit-exact reference baseline comparisons, use
        `bp.PackingTaskConfig.reference()`.
-   **`bp.stack(design)`**:
    -   Fast 1D strip-stacking layout utility for single-hub or linear-spine
        trees.

**SOTA Production Packing Config**:

```python
import bp_pipeline as bp

packing_cfg = bp.PackingTaskConfig(
    max_retries=30,
    max_cps_per_grid_size=2,
    max_number_of_cps=8,
    sweep_timeout_seconds=119.0,
    packing_config=bp.PackingConfig(
        traversal_mode='river_priority',
        include_straight_rivers=True,
        include_lshape_rivers=True,
        use_l_shaped_level_shifter=True,
        use_level_shifter=False,
        enforce_proximity_constraints=True,
        max_delta_combinations=1_000_000,
    ),
)
```

### Stage 3: Flat-Foldable Hinge Solving (`bp.solve`, `bp.solve_best`, `bp.solve_sweep`)

The hinge solver converts a `PackedCreasePattern` (with unassigned green
`Fold.HINGE` creases and 45° diagonal yellow `Fold.TRIANGLE` ridges) into a
globally flat-foldable Mountain/Valley crease pattern through 7 internal steps:

1.  **Packing CP** — Input grid layout with unassigned hinges and 45° diagonal
    ridges (`Fold.TRIANGLE`).
2.  **Unassigned Pleats** (`pleats.create_pleats`) — Propagates parallel pleat
    lines from every hinge across the sheet.
3.  **Assigned Pleats** (`pleats.assign_pleats`) — Assigns Mountain/Valley
    parities to hinges and pleats via partition-ordered search
    (`use_partition_order=True`) while enforcing local Kawasaki/Maekawa
    flat-foldability at every vertex.
4.  **Assigned Ridges** (`ridges.assign_ridges`) — Determines Mountain/Valley
    directions for all 45° diagonal ridges and pythagorean stretches.
5.  **Central Ridges** (`hinges.assign_central_ridges`) — Resolves ridges along
    the symmetry centerline ($x = 0.5$) and optionally removes redundant central
    creases (`remove_central_crease=True`).
6.  **+ Unassigned Pleats** — Reconciles any remaining neutral segments.
7.  **Final Solved CP** — Verifies global flat-foldability via the pure-Python
    flat-folder (`use_python_flat_folder=True`,
    `check_global_flat_foldability=True`).

**SOTA Production Solving Config (`PRODUCTION_SWEEP`)**: Sweeps over:

-   `hinges_from_stick_figure`: `[True, False]` (when `True`, uses 3D stick
    orientations via `up_down_method in ['azimuth', 'flaps_down']` to
    pre-identify flat hinges between opposite-pointing sticks).
-   `remove_central_crease`: `[True, False]`.
-   `max_steps=8000`, `use_partition_order=True`,
    `disallow_trapping_edge_flaps=True`, `tie_break_by_hinge_symmetry=True`.

--------------------------------------------------------------------------------

## 4. Exporting & Serialization (`codec` & `export`)

### 1. Lossless JSON Codec (`bp.dumps` / `bp.loads` / `bp.to_dict` / `bp.from_dict`)

Every bus object (`DesignTree`, `PackedCreasePattern`, `SolvedCreasePattern`,
`StickFigure`, `CreasePattern`) round-trips losslessly through JSON:

```python
json_str = bp.dumps(solved, indent=2)
restored_solved = bp.loads(json_str)
```

### 2. SVG Export (`.svg`)

```python
svg_str = bp.to_svg(solved)
```

### 3. FOLD Format Export (`.fold`)

Exports standard FOLD v1.2 JSON (`vertices_coords`, `edges_vertices`,
`edges_assignment`, `edges_foldAngle`) compatible with
[Origami Simulator](https://origamisimulator.org/) and Flat-Folder:

```python
fold_cp_dict = bp.to_fold(solved)
```

### 4. Box Pleating Studio Export (`.bps.json`)

Exports the tree and packed flap/river layout in the repo's
`BoxPleatingTreeData` (`.bps.json`) schema (`design.tree`, `design.layout`):

```python
bp_studio_dict = bp.to_bp_studio(packed)
```

### 5. HTML Contact Sheet (`bp.render_packing_grid`)

Renders a self-contained dark-mode HTML contact sheet comparing 2D isometric
stick figures, interactive packed flap/river/hinge overlays, and solved crease
patterns:

```python
html_doc = bp.render_packing_grid([solved], title='My Origami Results')
```

--------------------------------------------------------------------------------

## 5. End-to-End `bp-pipeline` CLI Runner

### Package CLI Validator, Solver, Shaper & Visual Renderer

To validate, pack, solve, 3D-shape, export (`.bps.json`, `.fold`,
`shaped_3d.fold`, `.svg`), and render `stick_figure_views.png`,
`pipeline_stages.png`, `shaped_3d_views.png`, and `contact_sheet.html` by
default:

```bash
bp-pipeline /abs/path/to/design.json \
  --output-dir /abs/path/to/output_dir \
  --check-symmetry
```
