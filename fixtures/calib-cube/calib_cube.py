# -*- coding: utf-8 -*-
#
# Parametric IMU calibration cube for FreeCAD 1.0 or newer. Uses only the
# Part and Mesh modules that come with FreeCAD, no external packages.
#
# Copyright (c) 2026 Gintaris Zimnickas, Mercury LT
# SPDX-License-Identifier: BSD-3-Clause
#
# A cube-shaped holder with flat, mutually perpendicular outer faces. The
# board lies inside, its axes parallel to the cube faces, fixed with screws
# into its mounting holes. The cube is a base (open box, printed opening
# up) and a lid (printed top face down), so both print without supports.
# The USB cable leaves through a U-slot in one wall and stays connected
# while the cube is turned.
#
# Run:
#   freecadcmd calib_cube.py                  (variant from VARIANT below)
#   freecadcmd calib_cube.py pse84            (variant from the command line)
#   or open it in FreeCAD: Macro > Macros... > Execute.
#
# Output (next to this file, in out/<variant>/):
#   calib_cube_<variant>_base.step/.stl, calib_cube_<variant>_lid.step/.stl
#
# Dimensions marked MEASURE are estimates: no mechanical drawing of the
# boards was available. Measure the board with a caliper and correct them
# before printing.
#
# Cube frame used below: Xc along the board's long side, Yc along its short
# side, Zc up (component side up, lid on top). Board origin = the board
# corner at (-Xc, -Yc); hole positions are measured from that corner.

import os
import sys

import FreeCAD as App
import Part

# ---------------------------------------------------------------------------
# Variant selection
# ---------------------------------------------------------------------------

VARIANT = "psc3_rab7"   # "psc3_rab7" or "pse84"

# Where the STEP/STL files go. Empty: an "out" folder next to this script
# (or "calib_cube_out" in your home folder when the script is pasted into
# the Python console). A full path, e.g. "C:/Users/me/Desktop/cube", is
# used as is.
OUTPUT_DIR = ""

# ---------------------------------------------------------------------------
# Common parameters (mm)
# ---------------------------------------------------------------------------

COMMON = {
    "wall": 6.0,             # wall, floor and lid thickness
    "clearance": 0.5,        # gap between board edge and inner wall
    "fit_tol": 0.25,         # FDM tolerance for lid lip / sliding fits
    "lid_lip_h": 2.0,        # alignment lip under the lid
    "lid_screw_d": 3.4,      # lid clearance hole (M3)
    "lid_screw_head_d": 6.0, # counterbore for M3 cylinder head
    "lid_screw_head_h": 3.2,
    "lid_pilot_d": 2.5,      # pilot hole in the base corners (M3 self-tapping)
    "lid_pilot_depth": 12.0,
    "board_pilot_d": 2.2,    # pilot hole in standoffs (M2.5 self-tapping)
    "standoff_d": 6.0,
    "label_size": 10.0,      # label text height
    "label_depth": 0.8,      # engraving depth
    "fonts": [               # first existing font is used for the labels
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ],
    "stl_deflection": 0.05,  # STL mesh linear deflection
}

# ---------------------------------------------------------------------------
# Board variants (mm). MEASURE = estimate, check on the real board.
# ---------------------------------------------------------------------------

VARIANTS = {
    # KIT_PSC3M5_EVK with a Rutronik RAB7-SENSORFUSION Arduino shield.
    "psc3_rab7": {
        "name": "KIT_PSC3M5_EVK + RAB7-SENSORFUSION",
        "board_l": 120.0,           # MEASURE: long side
        "board_w": 80.0,            # MEASURE: short side
        "board_t": 1.6,             # MEASURE: PCB thickness
        "below_h": 4.0,             # MEASURE: tallest part / pin under the board
        "above_h": 22.0,            # MEASURE: top of shield parts above the EVK
                                    # top (headers ~11 + shield PCB 1.6 + parts)
        "holes": [                  # MEASURE: mounting holes (x, y) from corner
            (4.0, 4.0), (116.0, 4.0), (4.0, 76.0), (116.0, 76.0),
        ],
        # USB cable slot (KitProg3 USB-C): wall, centre along that wall from
        # the board centre, slot width, and connector centre height above
        # the board top. MEASURE all four.
        "usb_wall": "-Xc",
        "usb_offset": 0.0,
        "usb_w": 14.0,
        "usb_z": 1.6,
        # Face labels = sensor axis that points out of the face. From the
        # BMI323 test on this board (2026-11-19): standing on the USB short
        # edge gives +Y up, so the USB end face is -Y; the long edges are
        # +-X; Z points up through the shield. VERIFY which long edge is +X.
        "labels": {"+Xc": "+Y", "-Xc": "-Y", "+Yc": "+X", "-Yc": "-X",
                   "+Zc": "+Z", "-Zc": "-Z"},
    },

    # KIT_PSE84_AI (on-board BMI270, BMM350, DPS368, SHT40).
    "pse84": {
        "name": "KIT_PSE84_AI",
        "board_l": 85.0,            # MEASURE
        "board_w": 56.0,            # MEASURE
        "board_t": 1.6,             # MEASURE
        "below_h": 4.0,             # MEASURE
        "above_h": 12.0,            # MEASURE: tallest part (camera connector,
                                    # Wi-Fi module, headers) above the PCB
        "holes": [                  # MEASURE
            (3.5, 3.5), (81.5, 3.5), (3.5, 52.5), (81.5, 52.5),
        ],
        "usb_wall": "-Xc",          # MEASURE: KitProg3 USB-C position
        "usb_offset": 0.0,
        "usb_w": 14.0,
        "usb_z": 1.6,
        # VERIFY on hardware: rest the cube on each face and check which
        # accelerometer axis reads -g (the axis of the face's label).
        "labels": {"+Xc": "+X", "-Xc": "-X", "+Yc": "+Y", "-Yc": "-Y",
                   "+Zc": "+Z", "-Zc": "-Z"},
    },
}

# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

V = App.Vector


def find_font(candidates):
    for f in candidates:
        if os.path.isfile(f):
            return f
    return None


def text_solid(text, font, size, depth):
    """Text in the XY plane, centred at the origin, from z=-depth to z=0."""
    chars = Part.makeWireString(text, font, size, 0)
    faces = []
    for wires in chars:
        if wires:
            faces.append(Part.Face(wires, "Part::FaceMakerBullseye"))
    if not faces:
        return None
    comp = Part.makeCompound(faces)
    bb = comp.BoundBox
    comp.translate(V(-bb.Center.x, -bb.Center.y, 0))
    return comp.extrude(V(0, 0, -depth))


def label_cut(shape, text, face_center, normal, c, font):
    """Engrave text into the face with outward 'normal' at 'face_center'."""
    if font is None or not text:
        return shape
    t = text_solid(text, font, c["label_size"], c["label_depth"])
    if t is None:
        return shape
    t.Placement = App.Placement(face_center,
                                App.Rotation(V(0, 0, 1), normal))
    return shape.cut(t)


def build(variant_key):
    p = VARIANTS[variant_key]
    c = COMMON

    wall = c["wall"]
    clr = c["clearance"]
    tol = c["fit_tol"]

    # Inner space needed by the board stack
    inner_l = p["board_l"] + 2 * clr
    inner_w = p["board_w"] + 2 * clr
    standoff_h = p["below_h"] + 1.0
    inner_h = standoff_h + p["board_t"] + p["above_h"] + c["lid_lip_h"] + clr

    # Cube: equal outer sides, so every face is a usable resting face
    inner = max(inner_l, inner_w, inner_h)
    side = inner + 2 * wall
    base_h = side - wall              # the lid is one wall thick

    # Board placement: centred in XY, on standoffs above the floor
    bx0 = (side - p["board_l"]) / 2.0
    by0 = (side - p["board_w"]) / 2.0
    board_bottom = wall + standoff_h
    board_top = board_bottom + p["board_t"]

    # --- Base: box with cavity, open at the top -------------------------
    base = Part.makeBox(side, side, base_h)
    cavity = Part.makeBox(inner, inner, base_h, V(wall, wall, wall))
    base = base.cut(cavity)

    # Standoffs with pilot holes at the board mounting holes
    for (hx, hy) in p["holes"]:
        cx, cy = bx0 + hx, by0 + hy
        post = Part.makeCylinder(c["standoff_d"] / 2.0, standoff_h,
                                 V(cx, cy, wall))
        base = base.fuse(post)
        pilot = Part.makeCylinder(c["board_pilot_d"] / 2.0, standoff_h + 1.0,
                                  V(cx, cy, wall))
        base = base.cut(pilot)

    # Lid screw pilots in the four wall corners
    lid_holes = [(wall / 2.0, wall / 2.0), (side - wall / 2.0, wall / 2.0),
                 (wall / 2.0, side - wall / 2.0),
                 (side - wall / 2.0, side - wall / 2.0)]
    for (hx, hy) in lid_holes:
        base = base.cut(Part.makeCylinder(
            c["lid_pilot_d"] / 2.0, c["lid_pilot_depth"],
            V(hx, hy, base_h - c["lid_pilot_depth"])))

    # USB cable U-slot: from just below the connector up to the base top
    slot_bottom = board_top + p["usb_z"] - p["usb_w"] / 2.0
    slot_h = base_h - slot_bottom + 1.0
    wall_key = p["usb_wall"]
    if wall_key in ("-Xc", "+Xc"):
        y0 = side / 2.0 + p["usb_offset"] - p["usb_w"] / 2.0
        x0 = -1.0 if wall_key == "-Xc" else side - wall - 1.0
        slot = Part.makeBox(wall + 2.0, p["usb_w"], slot_h,
                            V(x0, y0, slot_bottom))
    else:
        x0 = side / 2.0 + p["usb_offset"] - p["usb_w"] / 2.0
        y0 = -1.0 if wall_key == "-Yc" else side - wall - 1.0
        slot = Part.makeBox(p["usb_w"], wall + 2.0, slot_h,
                            V(x0, y0, slot_bottom))
    base = base.cut(slot)

    # --- Lid: plate with an alignment lip, printed top face down --------
    lid = Part.makeBox(side, side, wall, V(0, 0, base_h))
    lip_in = inner - 2 * tol
    lip = Part.makeBox(lip_in, lip_in, c["lid_lip_h"],
                       V(wall + tol, wall + tol, base_h - c["lid_lip_h"]))
    lip_hole = Part.makeBox(lip_in - 2 * 2.0, lip_in - 2 * 2.0,
                            c["lid_lip_h"],
                            V(wall + tol + 2.0, wall + tol + 2.0,
                              base_h - c["lid_lip_h"]))
    lid = lid.fuse(lip.cut(lip_hole))
    for (hx, hy) in lid_holes:
        lid = lid.cut(Part.makeCylinder(c["lid_screw_d"] / 2.0, wall,
                                        V(hx, hy, base_h)))
        lid = lid.cut(Part.makeCylinder(
            c["lid_screw_head_d"] / 2.0, c["lid_screw_head_h"],
            V(hx, hy, side - c["lid_screw_head_h"])))

    # The lip must not cover the USB slot
    lid = lid.cut(slot)

    # --- Face labels ----------------------------------------------------
    font = find_font(c["fonts"])
    if font is None:
        print("WARNING: no font found, labels are not engraved")
    m = side / 2.0
    lz = base_h * 0.3   # side labels in the lower third, below the USB slot
    lab = p["labels"]
    base = label_cut(base, lab["+Xc"], V(side, m, lz), V(1, 0, 0), c, font)
    base = label_cut(base, lab["-Xc"], V(0, m, lz), V(-1, 0, 0), c, font)
    base = label_cut(base, lab["+Yc"], V(m, side, lz), V(0, 1, 0), c, font)
    base = label_cut(base, lab["-Yc"], V(m, 0, lz), V(0, -1, 0), c, font)
    base = label_cut(base, lab["-Zc"], V(m, m, 0), V(0, 0, -1), c, font)
    lid = label_cut(lid, lab["+Zc"], V(m, m, side), V(0, 0, 1), c, font)

    info = {
        "side": side, "inner": inner, "base_h": base_h,
        "board_bottom": board_bottom, "standoff_h": standoff_h,
        "font": font,
    }
    return base, lid, info


def export(shape, path_noext, deflection):
    shape.exportStep(path_noext + ".step")
    try:
        import Mesh
        import MeshPart
        mesh = MeshPart.meshFromShape(Shape=shape,
                                      LinearDeflection=deflection,
                                      AngularDeflection=0.3,
                                      Relative=False)
        mesh.write(path_noext + ".stl")
    except ImportError:
        shape.exportStl(path_noext + ".stl")


def main():
    variant = VARIANT
    for arg in sys.argv[1:]:
        if arg in VARIANTS:
            variant = arg
        elif arg == "pse84":
            variant = "pse84"

    if OUTPUT_DIR:
        root = OUTPUT_DIR
    elif "__file__" in globals():
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    else:
        root = os.path.join(os.path.expanduser("~"), "calib_cube_out")
    outdir = os.path.join(root, variant)
    os.makedirs(outdir, exist_ok=True)

    base, lid, info = build(variant)
    for name, shape in (("base", base), ("lid", lid)):
        if not shape.isValid():
            print("WARNING: %s shape is not valid" % name)
        export(shape, os.path.join(outdir, "calib_cube_%s_%s" %
                                   (variant, name)),
               COMMON["stl_deflection"])

    print("%s: cube %.1f mm, inner %.1f mm, base height %.1f mm, "
          "board bottom %.1f mm above the outside bottom, font %s"
          % (VARIANTS[variant]["name"], info["side"], info["inner"],
             info["base_h"], info["board_bottom"], info["font"]))
    print("written to %s" % outdir)
    print("DONE")

    # Show the result when run inside the FreeCAD GUI
    if App.GuiUp:
        doc = App.newDocument("calib_cube_" + variant)
        doc.addObject("Part::Feature", "Base").Shape = base
        doc.addObject("Part::Feature", "Lid").Shape = lid
        doc.recompute()


main()
