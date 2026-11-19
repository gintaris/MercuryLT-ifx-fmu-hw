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
# Each dimension says where it comes from. ESTIMATE / MEASURE marks the
# values that are not taken from vendor design data; check them with a
# caliper before printing.
#
# Cube frame used below: Xc along the board's long side, Yc along its short
# side, Zc up (component side up, lid on top). Board coordinates: origin at
# the board corner (-Xc, -Yc), seen from the component side; all positions
# (holes, shield, USB) are in this frame.

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
    "board_pilot_d": 2.2,    # pilot hole in standoffs (M2.5 self-tapping);
    "standoff_d": 6.0,       # a variant can override both
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
    # KIT_PSC3M5_EVK (Rev 5.0) with a Rutronik RAB7-SENSORFUSION shield.
    #
    # Sources:
    #   [A] Infineon KIT_PSC3M5_EVK_Rev5.0_artwork.pdf (pcbdesigndata zip),
    #       1:1 plots: silkscreen top (outline), soldermask top (holes,
    #       pads). Checked: Arduino header pitch 2.54 mm, header rows
    #       48.30 mm apart (Uno: 48.26).
    #   [B] Infineon KIT_PSC3M5_EVK_Rev5.0_BOM.xlsm.
    #   [C] Rutronik RAB7-SENSORFUSION_PCB.step and Mechanical Drawing.PDF
    #       (github.com/RutronikSystemSolutions/RAB7_SENSORFUSION_Hardware_Files).
    "psc3_rab7": {
        "name": "KIT_PSC3M5_EVK + RAB7-SENSORFUSION",
        "board_l": 130.0,           # [A] outline 130.00 x 70.00, corners R2.54
        "board_w": 70.0,            # [A]
        "board_t": 1.6,             # ESTIMATE: nominal, not in [A]
        "below_h": 4.0,             # ESTIMATE: through-hole tails under the
                                    # board (no bottom-side parts in [A])
        # Top of the stack above the EVK top surface: EVK Arduino sockets
        # 8.5 [B: Wurth 61300811821 / 61301011821, height per Wurth data]
        # + RAB7 PCB 1.64 [C] + RAB7 stackable sockets 8.50 above the RAB7
        # [C] = 18.64. Tallest other EVK part: DC jack J20 PJ-102A, 11 [B].
        "above_h": 18.64,
        # Unplated mounting holes, 2.2 mm (M2) [A: soldermask top]
        "holes": [(3.97, 59.84), (3.97, 9.45), (114.02, 62.69)],
        "board_pilot_d": 1.6,       # M2 self-tapping into the printed post
        "standoff_d": 5.0,
        # Parts that reach beyond the board outline and must fit inside the
        # cavity, as (x0, y0, x1, y1) in board coordinates.
        # RAB7 outline 72.30 x 71.78 [C], placed by its header sockets on
        # the Uno grid of the EVK headers J1-J4 [A]: it overhangs the EVK
        # by about 0.9 mm on both long edges.
        "footprint": [(46.19, -0.95, 118.49, 70.83)],
        # KitProg3 USB-C J15 (Wurth 629722000214, top mount, right angle)
        # on the right short edge [A: pads at x 121.9-128.5, y 22.4-37.3];
        # usb_at = slot centre along that wall in board coordinates.
        "usb_wall": "+Xc",
        "usb_at": 29.85,
        "usb_w": 14.0,              # cable plug over-moulding + clearance
        "usb_z": 1.6,               # connector centre above the board top
        # Face labels = sensor axis that points out of the face.
        # BMI323 (U6 on the RAB7, 3.0 x 2.5 mm, long side along the board's
        # long side [C]) measured on this stack on 2026-11-19: USB edge down
        # gives +Y up, so +Y points away from the USB edge (board -x); Z is
        # up through the shield; the frame is right-handed (gyro Z sign
        # checked), so +X = Y x Z points to the long edge at board y = 70.
        "labels": {"+Xc": "-Y", "-Xc": "+Y", "+Yc": "+X", "-Yc": "-X",
                   "+Zc": "+Z", "-Zc": "-Z"},
    },

    # KIT_PSE84_AI (on-board BMI270, BMM350, DPS368, SHT40).
    # No layout data: the available Infineon PDF (630-60751-01) contains the
    # schematics only. All values are MEASURE estimates.
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
        "footprint": [],
        "usb_wall": "-Xc",          # MEASURE: KitProg3 USB-C position
        "usb_at": 28.0,             # MEASURE: along the wall, board coords
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

    pilot_d = p.get("board_pilot_d", c["board_pilot_d"])
    standoff_d = p.get("standoff_d", c["standoff_d"])

    # Footprint: the board plus everything that overhangs it (shield)
    fx0, fy0, fx1, fy1 = 0.0, 0.0, p["board_l"], p["board_w"]
    for (x0, y0, x1, y1) in p.get("footprint", []):
        fx0, fy0 = min(fx0, x0), min(fy0, y0)
        fx1, fy1 = max(fx1, x1), max(fy1, y1)

    # Inner space needed by the board stack
    inner_l = (fx1 - fx0) + 2 * clr
    inner_w = (fy1 - fy0) + 2 * clr
    standoff_h = p["below_h"] + 1.0
    inner_h = standoff_h + p["board_t"] + p["above_h"] + c["lid_lip_h"] + clr

    # Cube: equal outer sides, so every face is a usable resting face
    inner = max(inner_l, inner_w, inner_h)
    side = inner + 2 * wall
    base_h = side - wall              # the lid is one wall thick

    # Board placement: footprint centred in XY, board on standoffs
    bx0 = (side - (fx1 - fx0)) / 2.0 - fx0
    by0 = (side - (fy1 - fy0)) / 2.0 - fy0
    board_bottom = wall + standoff_h
    board_top = board_bottom + p["board_t"]

    # --- Base: box with cavity, open at the top -------------------------
    base = Part.makeBox(side, side, base_h)
    cavity = Part.makeBox(inner, inner, base_h, V(wall, wall, wall))
    base = base.cut(cavity)

    # Standoffs with pilot holes at the board mounting holes
    for (hx, hy) in p["holes"]:
        cx, cy = bx0 + hx, by0 + hy
        post = Part.makeCylinder(standoff_d / 2.0, standoff_h,
                                 V(cx, cy, wall))
        base = base.fuse(post)
        pilot = Part.makeCylinder(pilot_d / 2.0, standoff_h + 1.0,
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
        y0 = by0 + p["usb_at"] - p["usb_w"] / 2.0
        x0 = -1.0 if wall_key == "-Xc" else side - wall - 1.0
        slot = Part.makeBox(wall + 2.0, p["usb_w"], slot_h,
                            V(x0, y0, slot_bottom))
    else:
        x0 = bx0 + p["usb_at"] - p["usb_w"] / 2.0
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
