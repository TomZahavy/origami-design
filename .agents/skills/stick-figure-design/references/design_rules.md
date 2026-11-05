# Box-Pleating Stick Figure Design Rules

1.  **Tree Topology (No Cycles, Single Connected Component)**:

    -   Every stick connects two named joints (`start` and `end`).
    -   Do not form closed loops (`graph_has_cycle` must be `False`).
    -   All sticks must belong to a single connected tree (`graph_is_connected`
        must be `True`).
    -   After merging collinear degree-2 joints (`merge_linear_chains`), there
        must be **more than 2 sticks** (at least one branching joint of degree ≥
        3).

2.  **Bilateral Symmetry Across the YZ Plane**:

    -   Central axis sticks (`torso`, `body`, `neck`, `head`, `tail`) must lie
        in the YZ plane (`azimuth_angle` in `{0, 180, -180}` or
        `elevation_angle` in `{90, -90}`).
    -   Left/right limb pairs must mirror across the YZ plane:
        -   `left.azimuth_angle == -right.azimuth_angle`
        -   `left.elevation_angle == right.elevation_angle`
        -   `left.length == right.length`
        -   `left.width == right.width`

3.  **Symmetry Axis Width Parity**:

    -   All integer-width sticks on the symmetry axis must share the same parity
        (`width % 2`). Either use odd widths (`1`, `3`) for all axis sticks or
        even widths (`2`, `4`) for all axis sticks.
    -   Remember that terminal axis leaf flaps (`snout`, `head`, `tail`,
        `abdomen`) count as symmetry-axis sticks too — never mix `width: 2`
        rivers with `width: 1` `snout` or `tail` flaps.

4.  **Proportional Lengths & Non-Overlapping Limbs**:

    -   Keep `length` in `[1, 8]` (prefer `length >= 2` on terminal flaps such
        as ears, snout, and legs so shaping folds have room inside the flap);
        smaller integer lengths pack onto smaller grids and solve faster.
    -   Distribute limbs across separate joints (`hips`, `shoulders`, `head`)
        and fan out azimuth angles when multiple limbs share a joint (e.g.
        `60°`, `90°`, `120°`, `150°` for insect/arachnid legs).

5.  **River Equivalence-Class Budget & Hub Border-Slot Capacity**:

    -   **Keep River Equivalence Classes $\le 2$**: In `bp.pack()`, river
        candidate enumeration scales combinatorially with the number of river
        equivalence classes in `design.merged`, where **1 on-axis spine river
        counts as 1 class** and **1 mirrored left/right pair of off-axis rivers
        (e.g., `left_wing_arm` / `right_wing_arm`) counts as 1 class** (`3`
        rivers total). Prefer even integer lengths (`2`, `4`, `6`) for on-axis
        rivers in multi-river symmetric trees.
    -   **End-Hub Border-Slot Capacity ($\le 3$)**: An end hub (such as `head`,
        `prothorax`, or `hips`) has at most **3 symmetric border slots** on the
        square sheet perimeter (left corner, end edge cap, right corner).
        Attaching $\le 3$ flaps to an end hub prevents excess flaps from being
        trapped as interior pockets wrapped by U-shaped rivers.
    -   For 6- to 8-limb arthropods (spiders, scorpions, mantises, beetles),
        prefer a **1-river** backbone (converting tail/neck structures into
        degree-2 subdivided flaps) rather than trapping $\ge 4$ off-axis limbs
        on a middle hub between 2 rivers. For 10-limb decapods (crabs,
        lobsters), a perimeter-balanced **2-river** straight layout such as
        `[4, 2, 4]` flaps across front/mid/rear hubs saturates border slots
        cleanly without forcing U-river meanders.
    -   **Deterministic Sheet Top/Bottom Ordering**: In symmetric trees,
        `get_symmetric_connecting_joints()` orders hubs along the sheet's
        vertical symmetry line by comparing their incident left-limb azimuths
        (wider positive angles toward $180^\circ$ anchor at one end vs. narrower
        forward angles near $0^\circ$ at the other). Keep anterior lateral limbs
        angled forward ($45^\circ\text{–}90^\circ$) and posterior legs swept
        further back ($95^\circ\text{–}145^\circ$) for clean hub separation.

6.  **5-Flap Crown & Spine Width Sizing**:

    -   When an anterior hub (`crown`) has 5 flaps (e.g., `snout` +
        `left_ear`/`right_ear` + 2-segment antlers/horns), use `width >= 2`
        (e.g., `width: 2`) on all symmetry-axis sticks (`body`, `neck`, `snout`,
        `tail` — keeping even width parity) and `length >= 2` on the ears so the
        ears do not stretch into `1×4` vertical split-circle strips that fail
        `local_flat_foldability` during shaping.

7.  **3D Shaping & Folded Silhouette Alignment**:

    -   Always inspect `shaped_3d_views.png` (4-angle partial-dihedral 3D mesh
        render emitted by `bp-pipeline` / `bp.save_3d_turnaround`) as ground
        truth for the shaped 3D pose (`Iso`, `Side`, `Front`, `Top`), rather
        than judging 3D joints from a flat $180^\circ$ 2D kinematic reflection.
    -   When using 2 on-axis rivers (`body` and `neck`), keep both rivers
        co-axial in `(azimuth_angle, elevation_angle)` (e.g., `(0.0, 0.0)`).
    -   For multi-segment on-axis appendages (`tail_base` $\to$ `tail_tip`,
        `horn_base` $\to$ `horn_tip`), keep the basal segment collinear
        ($0^\circ$ bend) with the parent spine stick and put the upward
        elevation bend ($\Delta\psi \ge 37^\circ$) on the distal segment (or use
        $K = 2$ segments with $L_2 > L_1$ rather than $K = 3$) so the appendage
        projects cleanly outward in both 3D and 2D folded states.
    -   **Proximal Joint Clearance for Subdivided Limbs**: Space degree-2
        subdivision joints at least 2 grid units apart (`length >= 2`), and size
        each limb's proximal segment (`thigh`, `upper_arm`, `femur`) so the
        hub's azimuthal simple fold clears the first degree-2 bend joint:
        $L_{\text{upper}} > W \cdot \cot(\Delta\phi_{\text{base}} / 2)$, where
        $W$ is stick `width` and $\Delta\phi_{\text{base}}$ is the angular
        deflection between the limb and its packed axial direction on the sheet.
        Note that a flap's packed axial direction (`0°`, `±90°`, or `180°`) is
        chosen by `bp.pack()` based on whether the flap lands on a side border
        (`±90°`) or wraps onto the top/bottom border (`0°` / `180°`) — e.g.,
        `azimuth_angle: 122°` has $\Delta\phi_{\text{base}} = 32^\circ$ on a
        side border vs. $58^\circ$ on a top/bottom border! Therefore, for $W =
        1$ subdivided limbs whose azimuth falls near diagonal sectors
        ($30^\circ\text{–}60^\circ$ or $120^\circ\text{–}150^\circ$, where one
        border orientation yields $< 54^\circ$ deflection), prefer
        $L_{\text{upper}} \ge 3$ (or check `packing_cp.svg` if a limb lands in
        `shaping.discarded_elements`).
