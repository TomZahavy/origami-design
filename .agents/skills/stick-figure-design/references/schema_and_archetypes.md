# Stick Figure Schema, Coordinate System & Archetypes

## 1. JSON Schema Specification

A `StickFigure` JSON object represents a connected, acyclic 3D tree of sticks
(`Stick`) joined at named vertices (`start`, `end`).

```json
{
  "name": "cat",
  "category": "domestic animal",
  "complexity": 1,
  "color_top": [255, 196, 0],
  "color_bottom": [255, 196, 0],
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
    }
  ]
}
```

### Top-Level Fields (`StickFigure`)

Field          | Type              | Constraints                                  | Description
:------------- | :---------------- | :------------------------------------------- | :----------
`name`         | `string`          | Required, non-empty                          | Descriptive name of the subject.
`category`     | `string`          | Required                                     | Category label (e.g. `"animals"`, `"insects"`, `"humans"`, `"plants"`).
`complexity`   | `int`             | Required, `1..5`                             | `1` = simple (5–9 sticks), `2` = moderate (8–16 sticks), `3..5` = detailed/complex (12–25 sticks).
`color_top`    | `[int, int, int]` | RGB in `[0, 255]`                            | Top paper color `[R, G, B]`.
`color_bottom` | `[int, int, int]` | RGB in `[0, 255]`                            | Bottom paper color `[R, G, B]`.
`root`         | `string`          | Must match a stick `name`                    | Name of the root stick in `children`.
`children`     | `list[Stick]`     | At least 3 sticks after linear-chain merging | List of stick definitions forming a connected tree.

### Stick Fields (`Stick`)

Field             | Type           | Constraints                    | Description
:---------------- | :------------- | :----------------------------- | :----------
`name`            | `string`       | Unique across `children`       | Identifier for the stick (e.g. `"body"`, `"front_left_leg"`).
`start`           | `string`       | Joint name                     | Starting joint name (parent joint in BFS from `root`).
`end`             | `string`       | Joint name (`start != end`)    | Ending joint name.
`length`          | `int`          | Integer in `[1, 8]`            | Grid length of the flap or river.
`width`           | `float \| int` | Must be in `{0.5, 1, 2, 3, 4}` | Thickness/width of the stick. Collinear sticks must share the same width.
`azimuth_angle`   | `float`        | Degrees in `[-360, 360]`       | Counter-clockwise angle in the XY plane from North (`+Y`) at `start`.
`elevation_angle` | `float`        | Degrees in `[-90, 90]`         | Angle from the horizontal XY plane (`+90` = `+Z` up, `-90` = `-Z` down).
`shaping_flap`    | `bool`         | Always `false`                 | Reserved flag; set to `false`.

--------------------------------------------------------------------------------

## 2. 3D Coordinate System & Angle Math

When traversing a stick from its `start` joint to its `end` joint:

-   `xy_proj = length * cos(radians(elevation_angle))`
-   `dx = -xy_proj * sin(radians(azimuth_angle))`
-   `dy = xy_proj * cos(radians(azimuth_angle))`
-   `dz = length * sin(radians(elevation_angle))`

Key directions from `start` → `end`:

-   **Forward / North (`+Y`)**: `azimuth_angle = 0`, `elevation_angle = 0`
-   **Backward / South (`-Y`)**: `azimuth_angle = 180`, `elevation_angle = 0`
-   **Left (`-X`)**: `azimuth_angle = +90`, `elevation_angle = 0`
-   **Right (`+X`)**: `azimuth_angle = -90`, `elevation_angle = 0`
-   **Straight Up (`+Z`)**: `elevation_angle = +90` (`azimuth_angle = 0`)
-   **Straight Down (`-Z`)**: `elevation_angle = -90` (`azimuth_angle = 0`)

> **Important Traversal Rule**: Always orient `start` → `end` away from the
> `root` stick (so each child stick's `start` joint is already visited by its
> parent). Because angles are defined at `start`, consistent outward orientation
> makes bilateral symmetry (`+azimuth` vs `-azimuth`) straightforward and
> error-free.

--------------------------------------------------------------------------------

## 3. Topological & Packing Validity Rules

1.  **Connected Acyclic Tree**:
    -   The graph of `(start, end)` edges must be a single connected component
        with **no cycles**.
    -   After merging collinear degree-2 chains (`merge_linear_chains`), the
        tree must have **more than 2 sticks** (at least one branching joint of
        degree ≥ 3).
2.  **Collinear Chain Merging**:
    -   Two sticks sharing a degree-2 joint with identical 3D direction
        (`azimuth_angle` and `elevation_angle` within `0.1°`) are automatically
        merged into a single stick during packing.
    -   If you want a multi-segment limb (e.g. `upper_leg` → `knee` →
        `lower_leg`) to remain distinct in the 3D stick figure, give the
        segments different elevation or azimuth angles (e.g. `-60°` then
        `-75°`), while keeping aware that the box-pleating packer merges
        degree-2 chains into a single flap of summed length!
3.  **Bilateral Symmetry (`check_symmetry=True`)**:
    -   Sticks on the symmetry plane (`dx == 0`) have `azimuth_angle` in
        `{0, 180, -180}` (or `elevation_angle` in `{90, -90}`).
    -   Off-axis sticks must come in mirrored left/right pairs
        `(stick_L, stick_R)` attached to corresponding symmetric joints, with:
        -   `stick_L.length == stick_R.length`
        -   `stick_L.width == stick_R.width`
        -   `stick_L.elevation_angle == stick_R.elevation_angle`
        -   `stick_L.azimuth_angle == -stick_R.azimuth_angle`
    -   **Symmetry Axis Width Parity**: All integer-width sticks on the symmetry
        axis must have the same parity (`width % 2`). Do not mix `width: 1` and
        `width: 2` on the symmetry axis.

--------------------------------------------------------------------------------

## 4. Canonical Archetypes

### Archetype A: Quadruped (`cat`)

Central horizontal spine (`hips` → `shoulders`), head and front legs branching
from `shoulders`, rear legs and tail branching from `hips`.

```json
{
  "name": "cat",
  "category": "domestic animal",
  "complexity": 1,
  "color_top": [255, 196, 0],
  "color_bottom": [255, 196, 0],
  "root": "body",
  "children": [
    {"name": "body", "start": "hips", "end": "shoulders", "length": 4, "azimuth_angle": 0, "elevation_angle": 0, "width": 1, "shaping_flap": false},
    {"name": "head", "start": "shoulders", "end": "nose", "length": 1, "azimuth_angle": 0, "elevation_angle": 45, "width": 1, "shaping_flap": false},
    {"name": "front_left_leg", "start": "shoulders", "end": "front_left_paw", "length": 3, "azimuth_angle": 90, "elevation_angle": -70, "width": 1, "shaping_flap": false},
    {"name": "front_right_leg", "start": "shoulders", "end": "front_right_paw", "length": 3, "azimuth_angle": -90, "elevation_angle": -70, "width": 1, "shaping_flap": false},
    {"name": "rear_left_leg", "start": "hips", "end": "rear_left_paw", "length": 3, "azimuth_angle": 90, "elevation_angle": -70, "width": 1, "shaping_flap": false},
    {"name": "rear_right_leg", "start": "hips", "end": "rear_right_paw", "length": 3, "azimuth_angle": -90, "elevation_angle": -70, "width": 1, "shaping_flap": false},
    {"name": "tail", "start": "hips", "end": "tail_tip", "length": 3, "azimuth_angle": 180, "elevation_angle": 30, "width": 1, "shaping_flap": false}
  ]
}
```

### Archetype B: Biped (`human`)

Vertical torso (`hips` → `shoulders`), head and arms at `shoulders`, legs at
`hips`.

```json
{
  "name": "human",
  "category": "humans",
  "complexity": 1,
  "color_top": [247, 215, 216],
  "color_bottom": [247, 215, 216],
  "root": "torso",
  "children": [
    {"name": "torso", "start": "hips", "end": "shoulders", "azimuth_angle": 0, "length": 4, "elevation_angle": 90.0, "width": 1, "shaping_flap": false},
    {"name": "head", "start": "shoulders", "end": "head_top", "azimuth_angle": 0, "length": 1, "elevation_angle": 90.0, "width": 1, "shaping_flap": false},
    {"name": "right_arm", "start": "shoulders", "end": "right_hand", "azimuth_angle": -165, "length": 3, "elevation_angle": -20.0, "width": 1, "shaping_flap": false},
    {"name": "left_arm", "start": "shoulders", "end": "left_hand", "azimuth_angle": 165, "length": 3, "elevation_angle": -20.0, "width": 1, "shaping_flap": false},
    {"name": "right_leg", "start": "hips", "end": "right_foot", "azimuth_angle": -90, "length": 4, "elevation_angle": -60.0, "width": 1, "shaping_flap": false},
    {"name": "left_leg", "start": "hips", "end": "left_foot", "azimuth_angle": 90, "length": 4, "elevation_angle": -60.0, "width": 1, "shaping_flap": false}
  ]
}
```

### Archetype C: Multi-Limbed Insect / Arachnid (`scorpion`)

Segmented body with claws at `head`, legs distributed between `head` and
`abdomen_rear`, and a curved tail chain.

```json
{
  "name": "scorpion",
  "category": "insects",
  "complexity": 2,
  "color_top": [200, 150, 50],
  "color_bottom": [200, 150, 50],
  "root": "body",
  "children": [
    {"name": "body", "start": "abdomen_rear", "end": "head", "length": 4, "azimuth_angle": 0, "elevation_angle": 0, "width": 2, "shaping_flap": false},
    {"name": "claw_left_upper", "start": "head", "end": "cl_elbow", "length": 3, "azimuth_angle": 60, "elevation_angle": 0, "width": 1, "shaping_flap": false},
    {"name": "claw_left_lower", "start": "cl_elbow", "end": "cl_tip", "length": 2, "azimuth_angle": 30, "elevation_angle": 0, "width": 1, "shaping_flap": false},
    {"name": "claw_right_upper", "start": "head", "end": "cr_elbow", "length": 3, "azimuth_angle": -60, "elevation_angle": 0, "width": 1, "shaping_flap": false},
    {"name": "claw_right_lower", "start": "cr_elbow", "end": "cr_tip", "length": 2, "azimuth_angle": -30, "elevation_angle": 0, "width": 1, "shaping_flap": false},
    {"name": "tail_1", "start": "abdomen_rear", "end": "t1", "length": 2, "azimuth_angle": 180, "elevation_angle": 20, "width": 2, "shaping_flap": false},
    {"name": "tail_2", "start": "t1", "end": "t2", "length": 2, "azimuth_angle": 180, "elevation_angle": 50, "width": 2, "shaping_flap": false},
    {"name": "stinger", "start": "t2", "end": "stinger_tip", "length": 1, "azimuth_angle": 0, "elevation_angle": -60, "width": 2, "shaping_flap": false},
    {"name": "leg_1_left", "start": "abdomen_rear", "end": "l1l_tip", "length": 2, "azimuth_angle": 100, "elevation_angle": -20, "width": 1, "shaping_flap": false},
    {"name": "leg_2_left", "start": "abdomen_rear", "end": "l2l_tip", "length": 2, "azimuth_angle": 130, "elevation_angle": -20, "width": 1, "shaping_flap": false},
    {"name": "leg_3_left", "start": "head", "end": "l3l_tip", "length": 2, "azimuth_angle": 110, "elevation_angle": -20, "width": 1, "shaping_flap": false},
    {"name": "leg_4_left", "start": "head", "end": "l4l_tip", "length": 2, "azimuth_angle": 140, "elevation_angle": -20, "width": 1, "shaping_flap": false},
    {"name": "leg_1_right", "start": "abdomen_rear", "end": "l1r_tip", "length": 2, "azimuth_angle": -100, "elevation_angle": -20, "width": 1, "shaping_flap": false},
    {"name": "leg_2_right", "start": "abdomen_rear", "end": "l2r_tip", "length": 2, "azimuth_angle": -130, "elevation_angle": -20, "width": 1, "shaping_flap": false},
    {"name": "leg_3_right", "start": "head", "end": "l3r_tip", "length": 2, "azimuth_angle": -110, "elevation_angle": -20, "width": 1, "shaping_flap": false},
    {"name": "leg_4_right", "start": "head", "end": "l4r_tip", "length": 2, "azimuth_angle": -140, "elevation_angle": -20, "width": 1, "shaping_flap": false}
  ]
}
```

### Archetype D: Bird / Winged Creature (`crane_bird`)

Central body river (`hips` → `chest`), broad wings (`width: 2`) and curved
neck/beak chain at `chest`, legs and tail at `hips`.

```json
{
  "name": "crane_bird",
  "category": "animals",
  "complexity": 1,
  "color_top": [240, 244, 248],
  "color_bottom": [210, 220, 230],
  "root": "body",
  "children": [
    {"name": "body", "start": "hips", "end": "chest", "length": 2, "width": 1, "azimuth_angle": 0.0, "elevation_angle": 15.0, "shaping_flap": false},
    {"name": "neck", "start": "chest", "end": "head_joint", "length": 3, "width": 1, "azimuth_angle": 0.0, "elevation_angle": 70.0, "shaping_flap": false},
    {"name": "beak", "start": "head_joint", "end": "beak_tip", "length": 1, "width": 1, "azimuth_angle": 0.0, "elevation_angle": -10.0, "shaping_flap": false},
    {"name": "left_wing", "start": "chest", "end": "left_wing_tip", "length": 4, "width": 2, "azimuth_angle": 90.0, "elevation_angle": 25.0, "shaping_flap": false},
    {"name": "right_wing", "start": "chest", "end": "right_wing_tip", "length": 4, "width": 2, "azimuth_angle": -90.0, "elevation_angle": 25.0, "shaping_flap": false},
    {"name": "left_leg", "start": "hips", "end": "left_foot", "length": 3, "width": 1, "azimuth_angle": 90.0, "elevation_angle": -75.0, "shaping_flap": false},
    {"name": "right_leg", "start": "hips", "end": "right_foot", "length": 3, "width": 1, "azimuth_angle": -90.0, "elevation_angle": -75.0, "shaping_flap": false},
    {"name": "tail", "start": "hips", "end": "tail_tip", "length": 2, "width": 1, "azimuth_angle": 180.0, "elevation_angle": 25.0, "shaping_flap": false}
  ]
}
```

### Archetype E: Antlered / Horned Subject (`stag_deer` — River Budget Pattern)

To avoid combinatorial river explosion (keep river equivalence classes $\le 2$),
represent curved antlers or horns as **multi-segment degree-2 chains**
(`antler_base` → `antler_tip` with distinct angles) branching from `crown`
rather than adding degree-3 forks mid-antler. Keep `body` and `neck` co-axial in
`(azimuth_angle, elevation_angle)` (`0.0, 0.0`) with `width: 2` on all
symmetry-axis sticks (`body`, `neck`, `snout`, `tail`) and `length: 2` on any
ears at `crown` so 3D shaping (`bp.shape`) succeeds with 100% local
flat-foldability:

```json
{
  "name": "stag_deer",
  "category": "animals",
  "complexity": 3,
  "color_top": [145, 78, 36],
  "color_bottom": [244, 232, 204],
  "root": "body",
  "children": [
    {"name": "body", "start": "hips", "end": "shoulders", "length": 4, "width": 2, "azimuth_angle": 0.0, "elevation_angle": 0.0, "shaping_flap": false},
    {"name": "neck", "start": "shoulders", "end": "crown", "length": 2, "width": 2, "azimuth_angle": 0.0, "elevation_angle": 0.0, "shaping_flap": false},
    {"name": "snout", "start": "crown", "end": "nose", "length": 2, "width": 2, "azimuth_angle": 0.0, "elevation_angle": 0.0, "shaping_flap": false},
    {"name": "left_ear", "start": "crown", "end": "left_ear_tip", "length": 2, "width": 1, "azimuth_angle": 95.0, "elevation_angle": 25.0, "shaping_flap": false},
    {"name": "right_ear", "start": "crown", "end": "right_ear_tip", "length": 2, "width": 1, "azimuth_angle": -95.0, "elevation_angle": 25.0, "shaping_flap": false},
    {"name": "left_antler_base", "start": "crown", "end": "left_antler_mid", "length": 2, "width": 1, "azimuth_angle": 65.0, "elevation_angle": 20.0, "shaping_flap": false},
    {"name": "left_antler_tip", "start": "left_antler_mid", "end": "left_antler_end", "length": 2, "width": 1, "azimuth_angle": 65.0, "elevation_angle": 65.0, "shaping_flap": false},
    {"name": "right_antler_base", "start": "crown", "end": "right_antler_mid", "length": 2, "width": 1, "azimuth_angle": -65.0, "elevation_angle": 20.0, "shaping_flap": false},
    {"name": "right_antler_tip", "start": "right_antler_mid", "end": "right_antler_end", "length": 2, "width": 1, "azimuth_angle": -65.0, "elevation_angle": 65.0, "shaping_flap": false},
    {"name": "front_left_leg", "start": "shoulders", "end": "front_left_hoof", "length": 4, "width": 1, "azimuth_angle": 95.0, "elevation_angle": -35.0, "shaping_flap": false},
    {"name": "front_right_leg", "start": "shoulders", "end": "front_right_hoof", "length": 4, "width": 1, "azimuth_angle": -95.0, "elevation_angle": -35.0, "shaping_flap": false},
    {"name": "rear_left_leg", "start": "hips", "end": "rear_left_hoof", "length": 4, "width": 1, "azimuth_angle": 100.0, "elevation_angle": -35.0, "shaping_flap": false},
    {"name": "rear_right_leg", "start": "hips", "end": "rear_right_hoof", "length": 4, "width": 1, "azimuth_angle": -100.0, "elevation_angle": -35.0, "shaping_flap": false},
    {"name": "tail", "start": "hips", "end": "tail_tip", "length": 2, "width": 2, "azimuth_angle": 180.0, "elevation_angle": 0.0, "shaping_flap": false}
  ]
}
```

### Archetype F: High-Complexity Winged Dragon (`winged_dragon` — Off-Axis Wing Rivers)

Combines **1 central spine river** (`body`) with **1 mirrored pair of off-axis
limb rivers** (`left_wing_arm` / `right_wing_arm`) — totaling **2 river
equivalence classes** (`3` rivers) — to support 3-fingered articulated bat wings
alongside subdivided legs, a raised neck/snout chain, and a curved tail
(`21` sticks, `12` packed flaps, `26x26` grid, `0` discarded shaping elements):

```json
{
  "name": "winged_dragon",
  "category": "fantasy",
  "complexity": 4,
  "color_top": [155, 28, 28],
  "color_bottom": [242, 214, 162],
  "root": "body",
  "children": [
    {"name": "body", "start": "hips", "end": "shoulders", "length": 4, "width": 2, "azimuth_angle": 0.0, "elevation_angle": 0.0, "shaping_flap": false},
    {"name": "neck", "start": "shoulders", "end": "head_joint", "length": 3, "width": 2, "azimuth_angle": 0.0, "elevation_angle": 55.0, "shaping_flap": false},
    {"name": "snout", "start": "head_joint", "end": "nose", "length": 2, "width": 2, "azimuth_angle": 0.0, "elevation_angle": -5.0, "shaping_flap": false},
    {"name": "left_wing_arm", "start": "shoulders", "end": "left_wrist", "length": 2, "width": 1, "azimuth_angle": 85.0, "elevation_angle": 35.0, "shaping_flap": false},
    {"name": "right_wing_arm", "start": "shoulders", "end": "right_wrist", "length": 2, "width": 1, "azimuth_angle": -85.0, "elevation_angle": 35.0, "shaping_flap": false},
    {"name": "left_wing_lead", "start": "left_wrist", "end": "left_wing_lead_tip", "length": 3, "width": 1, "azimuth_angle": 45.0, "elevation_angle": 25.0, "shaping_flap": false},
    {"name": "right_wing_lead", "start": "right_wrist", "end": "right_wing_lead_tip", "length": 3, "width": 1, "azimuth_angle": -45.0, "elevation_angle": 25.0, "shaping_flap": false},
    {"name": "left_wing_mid", "start": "left_wrist", "end": "left_wing_mid_tip", "length": 3, "width": 1, "azimuth_angle": 90.0, "elevation_angle": 10.0, "shaping_flap": false},
    {"name": "right_wing_mid", "start": "right_wrist", "end": "right_wing_mid_tip", "length": 3, "width": 1, "azimuth_angle": -90.0, "elevation_angle": 10.0, "shaping_flap": false},
    {"name": "left_wing_trail", "start": "left_wrist", "end": "left_wing_trail_tip", "length": 2, "width": 1, "azimuth_angle": 135.0, "elevation_angle": -10.0, "shaping_flap": false},
    {"name": "right_wing_trail", "start": "right_wrist", "end": "right_wing_trail_tip", "length": 2, "width": 1, "azimuth_angle": -135.0, "elevation_angle": -10.0, "shaping_flap": false},
    {"name": "front_left_upper", "start": "shoulders", "end": "front_left_elbow", "length": 2, "width": 1, "azimuth_angle": 75.0, "elevation_angle": -45.0, "shaping_flap": false},
    {"name": "front_left_lower", "start": "front_left_elbow", "end": "front_left_claw", "length": 2, "width": 1, "azimuth_angle": 55.0, "elevation_angle": -85.0, "shaping_flap": false},
    {"name": "front_right_upper", "start": "shoulders", "end": "front_right_elbow", "length": 2, "width": 1, "azimuth_angle": -75.0, "elevation_angle": -45.0, "shaping_flap": false},
    {"name": "front_right_lower", "start": "front_right_elbow", "end": "front_right_claw", "length": 2, "width": 1, "azimuth_angle": -55.0, "elevation_angle": -85.0, "shaping_flap": false},
    {"name": "rear_left_upper", "start": "hips", "end": "rear_left_knee", "length": 2, "width": 1, "azimuth_angle": 105.0, "elevation_angle": -45.0, "shaping_flap": false},
    {"name": "rear_left_lower", "start": "rear_left_knee", "end": "rear_left_claw", "length": 2, "width": 1, "azimuth_angle": 105.0, "elevation_angle": -85.0, "shaping_flap": false},
    {"name": "rear_right_upper", "start": "hips", "end": "rear_right_knee", "length": 2, "width": 1, "azimuth_angle": -105.0, "elevation_angle": -45.0, "shaping_flap": false},
    {"name": "rear_right_lower", "start": "rear_right_knee", "end": "rear_right_claw", "length": 2, "width": 1, "azimuth_angle": -105.0, "elevation_angle": -85.0, "shaping_flap": false},
    {"name": "tail_base", "start": "hips", "end": "tail_mid", "length": 2, "width": 2, "azimuth_angle": 180.0, "elevation_angle": 0.0, "shaping_flap": false},
    {"name": "tail_tip", "start": "tail_mid", "end": "tail_end", "length": 3, "width": 2, "azimuth_angle": 180.0, "elevation_angle": 45.0, "shaping_flap": false}
  ]
}
```
