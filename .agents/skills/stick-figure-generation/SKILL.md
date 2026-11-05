---
name: stick-figure-generation
description: Programmatic Python validation, spherical coordinate equations, and river equivalence-class math for 3D origami stick figures (`StickFigure` / `DesignTree`) in `bp_pipeline`. Complements `stick-figure-design` when generating or manipulating stick figures directly in Python.
---

# Programmatic Stick-Figure Generation & Coordinate Math

An origami **Stick Figure** (`bp.StickFigure` / `bp.DesignTree`) is a 3D metric
tree specifying both **box-pleating flap/river lengths** (`bp.pack`) and **3D
joint orientations** (`bp.shape`).

For the end-to-end CLI authoring workflow, canonical design rules, and complex
multi-river archetypes (including the 2-river-class `winged_dragon`), see:

-   [`../stick-figure-design/SKILL.md`](../stick-figure-design/SKILL.md)
-   [`../stick-figure-design/references/design_rules.md`](../stick-figure-design/references/design_rules.md)
-   [`../stick-figure-design/references/schema_and_archetypes.md`](../stick-figure-design/references/schema_and_archetypes.md)

--------------------------------------------------------------------------------

## 1. Programmatic Validation & Solving in Python

```python
import bp_pipeline as bp
from bp_pipeline.stick_figures import graph_checks

errors = graph_checks.prevalidate(stick_figure_dict, check_symmetry=True)
assert not errors, errors
design = bp.prepare(stick_figure_dict)
assert graph_checks.is_valid_stick_figure(design.source)
packed = bp.pack(design)
solved = bp.solve_best(packed)
shaped = bp.shape(solved)
```

--------------------------------------------------------------------------------

## 2. Spherical Coordinate System (`Stick.get_coords`)

Every stick is a directed 3D vector of integer `length` $r \in [1, 8]$ from
joint `start` to joint `end` (always orient `start` $\to$ `end` outward away
from `root`):

$$
\begin{aligned}
\text{xy\_proj} &= r \cos(\psi), & \Delta z &= r \sin(\psi), \\
\Delta x &= -\text{xy\_proj} \sin(\phi), & \Delta y &= \text{xy\_proj} \cos(\phi)
\end{aligned}
$$

where $\phi = \text{azimuth\_angle} \in [-360^\circ, 360^\circ]$ and $\psi =
\text{elevation\_angle} \in [-90^\circ, 90^\circ]$ (in degrees).

Direction (from `start` to `end`)    | `elevation_angle` ($\psi$) | `azimuth_angle` ($\phi$)
:----------------------------------- | :------------------------: | :----------------------:
Straight Up ($+z$)                   | `90`                       | `0`
Straight Down ($-z$)                 | `-90`                      | `0`
Forward Horizontal ($+y$, North)     | `0`                        | `0`
Backward Horizontal ($-y$, South)    | `0`                        | `180`
Left Horizontal ($-x$, West)         | `0`                        | `90`
Right Horizontal ($+x$, East)        | `0`                        | `-90`
Forward-Up $45^\circ$ (neck/snout)   | `45`                       | `0`
Backward-Up $30^\circ$ (raised tail) | `30`                       | `180`
Downward-Left Splayed Leg            | `-70`                      | `90`
Downward-Right Splayed Leg           | `-70`                      | `-90`

--------------------------------------------------------------------------------

## 3. Summary of Key Structural Invariants

See [`../stick-figure-design/references/design_rules.md`](../stick-figure-design/references/design_rules.md)
for full geometric derivations; when generating stick figures programmatically,
always check:

1.  **Connected Acyclic Tree & $\ge 3$ Merged Sticks**: `|V| = |E| + 1`, unique
    `snake_case` stick names, `root` on the symmetry axis, and $> 2$ sticks in
    `design.merged.children`.
2.  **Degree-2 Subdivisions Merge Free in Packing**: Chains connected at
    degree-2 joints merge into a single flap of length $\sum L_i$ in
    `design.merged` while preserving 3D bend joints in `design.source` for
    `bp.shape()`. Keep each subdivided segment `length >= 2` and bend angles
    $\ge 37^\circ$ (`< 12°` bends are skipped; `12°–37°` bends clip slope to
    `3.0`).
3.  **River Equivalence-Class Budget ($\le 2$ Classes)**: `1` on-axis spine
    river counts as `1` class, and `1` mirrored left/right pair of off-axis
    rivers (e.g., `left_wing_arm` / `right_wing_arm`) counts as `1` class (`3`
    rivers total). Keeping `design.merged` to $\le 2$ river classes avoids
    combinatorial river-search timeouts.
4.  **Symmetry-Axis Width Parity & End-Hub Capacity**: All integer-width sticks
    on the symmetry axis (including terminal `snout`/`tail` flaps) must share
    the same parity (`width % 2`). Keep terminal hubs to $\le 3$ flaps (or use
    `width >= 2` on all axis sticks + `length >= 2` ears for 5-flap crowns).
5.  **Proximal Joint Clearance**: Ensure $L_{\text{upper}} > W
    \cot(\Delta\phi_{\text{base}} / 2)$ (prefer $L_{\text{upper}} \ge 3$ on $W =
    1$ limbs at diagonal azimuths $30^\circ\text{–}60^\circ$ or
    $120^\circ\text{–}150^\circ$, since packed border direction may be either
    $\pm 90^\circ$ or $0^\circ / 180^\circ$).

--------------------------------------------------------------------------------

## 4. Minimal Symmetric JSON Example

```json
{
  "name": "standing_wolf",
  "category": "animals",
  "complexity": 2,
  "color_top": [180, 180, 190],
  "color_bottom": [230, 230, 235],
  "root": "body",
  "children": [
    {
      "name": "body",
      "start": "hips",
      "end": "shoulders",
      "length": 4,
      "width": 1,
      "azimuth_angle": 0.0,
      "elevation_angle": 0.0,
      "shaping_flap": false
    },
    {
      "name": "head",
      "start": "shoulders",
      "end": "nose",
      "length": 2,
      "width": 1,
      "azimuth_angle": 0.0,
      "elevation_angle": 45.0,
      "shaping_flap": false
    },
    {
      "name": "front_left_leg",
      "start": "shoulders",
      "end": "front_left_paw",
      "length": 3,
      "width": 1,
      "azimuth_angle": 90.0,
      "elevation_angle": -70.0,
      "shaping_flap": false
    },
    {
      "name": "front_right_leg",
      "start": "shoulders",
      "end": "front_right_paw",
      "length": 3,
      "width": 1,
      "azimuth_angle": -90.0,
      "elevation_angle": -70.0,
      "shaping_flap": false
    },
    {
      "name": "rear_left_leg",
      "start": "hips",
      "end": "rear_left_paw",
      "length": 3,
      "width": 1,
      "azimuth_angle": 90.0,
      "elevation_angle": -70.0,
      "shaping_flap": false
    },
    {
      "name": "rear_right_leg",
      "start": "hips",
      "end": "rear_right_paw",
      "length": 3,
      "width": 1,
      "azimuth_angle": -90.0,
      "elevation_angle": -70.0,
      "shaping_flap": false
    },
    {
      "name": "tail",
      "start": "hips",
      "end": "tail_tip",
      "length": 3,
      "width": 1,
      "azimuth_angle": 180.0,
      "elevation_angle": 30.0,
      "shaping_flap": false
    }
  ]
}
```
