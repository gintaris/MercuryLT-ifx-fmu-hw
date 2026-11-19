# -*- coding: utf-8 -*-
#
# Parametric IMU calibration cube for FreeCAD 1.0 or newer. Uses only the
# Part and Mesh modules that come with FreeCAD, no external packages.
#
# Copyright (c) 2026 Gintaris Zimnickas, Mercury LT
# SPDX-License-Identifier: BSD-3-Clause
#
# A cube-shaped holder with flat, mutually perpendicular outer faces. The
# board lies inside with its axes parallel to the cube faces:
#
#   - it stands on its own stick-on rubber feet in shallow pockets in the
#     floor (no screws: the board holes carry the feet);
#   - rails on the floor around the PCB outline locate it in X and Y;
#   - pins under the lid press on bare PCB spots through small foam pads
#     and hold it in Z.
#
# The cube is a base (open box, printed opening up) and a lid (printed top
# face down), so both print without supports. The USB cable leaves
# through a U-slot in one wall and stays connected while the cube is
# turned.
#
# Run:
#   freecadcmd calib_cube.py                  (variant from VARIANT below)
#   freecadcmd calib_cube.py pse84            (variant from the command line)
#   or in FreeCAD: Macro > Macros... > Execute.
#
# Each dimension says where it comes from. MEASURE / ESTIMATE marks the
# values that are not taken from vendor design data or measured on the
# board; check them with a caliper before printing.
#
# Cube frame: Xc along the board's long side, Yc along its short side, Zc
# up (component side up, lid on top). Board coordinates: origin at the PCB
# corner (-Xc, -Yc), seen from the component side; all positions (feet,
# shield, USB, press points) are in this frame. Heights are measured from
# the bottom of the rubber feet.

import os
import sys

import FreeCAD as App
import Part

# ---------------------------------------------------------------------------
# Variant selection and output
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
    "clearance": 0.5,        # gap between the board stack and inner walls
    "fit_tol": 0.25,         # FDM tolerance for the lid lip
    "lid_lip_h": 2.0,        # alignment lip under the lid
    "lid_screw_d": 3.4,      # lid clearance hole (M3)
    "lid_screw_head_d": 6.0, # counterbore for an M3 cylinder head
    "lid_screw_head_h": 3.2,
    "lid_pilot_d": 2.5,      # pilot hole in the base corners (M3 self-tapping)
    "lid_pilot_depth": 12.0,
    "foot_pocket_depth": 1.0,  # pockets in the floor for the rubber feet
    "foot_pocket_clear": 0.6,  # pocket diameter = foot diameter + this
    "rail_w": 2.0,           # XY locating rails around the PCB outline
    "rail_clear": 0.3,       # gap between PCB edge and rail
    "rail_above": 1.0,       # rail top above the PCB top surface
    "rail_corner_gap": 4.0,  # rails stop this far from the PCB corners
    "press_d": 8.0,          # hold-down pins under the lid
    "foam_t": 3.0,           # gap left for a foam pad on each pin end
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
# Board variants (mm)
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
    #   [U] Measured by the user on the real stack, 2026-11-19.
    "psc3_rab7": {
        "name": "KIT_PSC3M5_EVK + RAB7-SENSORFUSION",
        "board_l": 130.0,           # [A] outline 130.00 x 70.00, corners R2.54
        "board_w": 70.0,            # [A]
        "board_t": 1.6,             # ESTIMATE: nominal, not in [A]
        # Bottom of the rubber feet to the top of the RAB7 stackable
        # sockets [U].
        "stack_h": 29.0,
        # Stick-on rubber feet. The board's three unplated 2.2 mm holes
        # [A: soldermask top] carry feet; the 4th position is a likely
        # corner. MEASURE diameter, height and positions.
        "feet": [(3.97, 59.84), (3.97, 9.45), (114.02, 62.69),
                 (114.02, 9.45)],
        "foot_d": 8.0,              # MEASURE
        # MEASURE. Default = stack_h - board_t - 18.64, where 18.64 is the
        # stack above the EVK top: EVK Arduino sockets 8.5 [B: Wurth
        # 61300811821 / 61301011821] + RAB7 PCB 1.64 [C] + RAB7 sockets
        # 8.50 [C].
        "foot_h": 8.76,
        # Parts that reach beyond the PCB outline and must fit in the
        # cavity, as (x0, y0, x1, y1). RAB7 outline 72.30 x 71.78 [C],
        # placed by its sockets on the Uno grid of the EVK headers J1-J4
        # [A]; it overhangs both long EVK edges by about 0.9 mm.
        "footprint": [(46.19, -0.95, 118.49, 70.83)],
        # Hold-down: the lid pins press on the RAB7 PCB top (stack_h - 8.50
        # [C]) at component-free spots [C: >= 6.5 mm from any part at the
        # long-edge midpoints, >= 16 mm at the side points]. Not on the
        # stackable sockets and not on parts.
        "press": [(82.34, 2.05), (82.34, 67.83), (49.19, 34.94),
                  (115.49, 34.94)],
        "press_z": 29.0 - 8.50,     # contact surface above the feet bottom
        # KitProg3 USB-C J15 (Wurth 629722000214, top mount, right angle)
        # on the right short edge [A: pads x 121.9-128.5, y 22.4-37.3].
        "usb_wall": "+Xc",
        "usb_at": 29.85,            # slot centre along that wall
        "usb_w": 14.0,              # cable plug over-moulding + clearance
        "usb_z": 1.6,               # connector centre above the PCB top
        # Face labels = sensor axis that points out of the face. BMI323
        # (U6 on the RAB7, 3.0 x 2.5 mm, long side along the board's long
        # side [C]) measured on this stack on 2026-11-19: USB edge down
        # gives +Y up, so +Y points away from the USB edge (board -x); Z is
        # up through the shield; the frame is right-handed (gyro Z sign
        # checked), so +X = Y x Z points to the long edge at board y = 70.
        "labels": {"+Xc": "-Y", "-Xc": "+Y", "+Yc": "+X", "-Yc": "-X",
                   "+Zc": "+Z", "-Zc": "-Z"},
    },

    # KIT_PSE84_AI (on-board BMI270, BMM350, DPS368, SHT40). No layout
    # data: the available Infineon PDF (630-60751-01) contains the
    # schematics only. All values are MEASURE estimates.
    "pse84": {
        "name": "KIT_PSE84_AI",
        "board_l": 85.0,            # MEASURE
        "board_w": 56.0,            # MEASURE
        "board_t": 1.6,             # MEASURE
        "stack_h": 18.0,            # MEASURE: feet bottom to tallest part
        "feet": [(3.5, 3.5), (81.5, 3.5), (3.5, 52.5), (81.5, 52.5)],
        "foot_d": 8.0,              # MEASURE
        "foot_h": 4.0,              # MEASURE
        "footprint": [],
        # MEASURE: bare PCB spots near the corners; contact on the PCB top
        "press": [(6.0, 6.0), (79.0, 6.0), (6.0, 50.0), (79.0, 50.0)],
        "press_z": 4.0 + 1.6,       # foot_h + board_t
        "usb_wall": "-Xc",          # MEASURE: KitProg3 USB-C position
        "usb_at": 28.0,             # MEASURE
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


def rails(p, c, bx0, by0, z0, z1):
    """Locating rails around the PCB outline, open at the USB connector."""
    L, W = p["board_l"], p["board_w"]
    g, w, k = c["rail_clear"], c["rail_w"], c["rail_corner_gap"]
    h = z1 - z0
    usb_lo = p["usb_at"] - p["usb_w"] / 2.0
    usb_hi = p["usb_at"] + p["usb_w"] / 2.0
    segs = []

    def span(a0, a1, wall_key):
        """Split a rail span [a0, a1] around the USB opening."""
        if wall_key != p["usb_wall"]:
            return [(a0, a1)]
        out = []
        if usb_lo - a0 > 2.0:
            out.append((a0, usb_lo))
        if a1 - usb_hi > 2.0:
            out.append((usb_hi, a1))
        return out

    for (a0, a1) in span(k, L - k, "-Yc"):
        segs.append(Part.makeBox(a1 - a0, w, h, V(bx0 + a0, by0 - g - w, z0)))
    for (a0, a1) in span(k, L - k, "+Yc"):
        segs.append(Part.makeBox(a1 - a0, w, h, V(bx0 + a0, by0 + W + g, z0)))
    for (a0, a1) in span(k, W - k, "-Xc"):
        segs.append(Part.makeBox(w, a1 - a0, h, V(bx0 - g - w, by0 + a0, z0)))
    for (a0, a1) in span(k, W - k, "+Xc"):
        segs.append(Part.makeBox(w, a1 - a0, h, V(bx0 + L + g, by0 + a0, z0)))
    return segs


def build(variant_key):
    p = VARIANTS[variant_key]
    c = COMMON

    wall = c["wall"]
    clr = c["clearance"]
    tol = c["fit_tol"]

    # Footprint: PCB plus overhanging parts, plus the rails around the PCB
    rr = c["rail_clear"] + c["rail_w"]
    fx0, fy0 = -rr, -rr
    fx1, fy1 = p["board_l"] + rr, p["board_w"] + rr
    for (x0, y0, x1, y1) in p.get("footprint", []):
        fx0, fy0 = min(fx0, x0), min(fy0, y0)
        fx1, fy1 = max(fx1, x1), max(fy1, y1)

    # Heights, from the bottom of the feet (which sit in the floor pockets)
    feet_z = wall - c["foot_pocket_depth"]
    pcb_top = feet_z + p["foot_h"] + p["board_t"]
    stack_top = feet_z + p["stack_h"]

    inner_l = (fx1 - fx0) + 2 * clr
    inner_w = (fy1 - fy0) + 2 * clr
    inner_h = (stack_top - wall) + c["foam_t"] + c["lid_lip_h"] + clr

    # Cube: equal outer sides, so every face is a usable resting face
    inner = max(inner_l, inner_w, inner_h)
    side = inner + 2 * wall
    base_h = side - wall              # the lid is one wall thick

    # Footprint centred in XY
    bx0 = (side - (fx1 - fx0)) / 2.0 - fx0
    by0 = (side - (fy1 - fy0)) / 2.0 - fy0

    # --- Base: box with cavity, open at the top -------------------------
    base = Part.makeBox(side, side, base_h)
    base = base.cut(Part.makeBox(inner, inner, base_h, V(wall, wall, wall)))

    # Pockets for the rubber feet
    pocket_r = (p["foot_d"] + c["foot_pocket_clear"]) / 2.0
    for (fx, fy) in p["feet"]:
        base = base.cut(Part.makeCylinder(pocket_r,
                                          c["foot_pocket_depth"] + 0.01,
                                          V(bx0 + fx, by0 + fy, feet_z)))

    # Rails up to just above the PCB top
    for seg in rails(p, c, bx0, by0, wall, pcb_top + c["rail_above"]):
        base = base.fuse(seg)

    # Lid screw pilots in the four wall corners
    lid_holes = [(wall / 2.0, wall / 2.0), (side - wall / 2.0, wall / 2.0),
                 (wall / 2.0, side - wall / 2.0),
                 (side - wall / 2.0, side - wall / 2.0)]
    for (hx, hy) in lid_holes:
        base = base.cut(Part.makeCylinder(
            c["lid_pilot_d"] / 2.0, c["lid_pilot_depth"],
            V(hx, hy, base_h - c["lid_pilot_depth"])))

    # USB cable U-slot: from just below the connector up to the base top
    slot_bottom = pcb_top + p["usb_z"] - p["usb_w"] / 2.0
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

    # --- Lid: plate with an alignment lip and hold-down pins -------------
    lid = Part.makeBox(side, side, wall, V(0, 0, base_h))
    lip_in = inner - 2 * tol
    lip = Part.makeBox(lip_in, lip_in, c["lid_lip_h"],
                       V(wall + tol, wall + tol, base_h - c["lid_lip_h"]))
    lip_hole = Part.makeBox(lip_in - 4.0, lip_in - 4.0, c["lid_lip_h"],
                            V(wall + tol + 2.0, wall + tol + 2.0,
                              base_h - c["lid_lip_h"]))
    lid = lid.fuse(lip.cut(lip_hole))

    # Pins end foam_t above the contact surface; a foam pad glued to the
    # pin end gives the compliance.
    pin_bottom = feet_z + p["press_z"] + c["foam_t"]
    for (px, py) in p["press"]:
        lid = lid.fuse(Part.makeCylinder(c["press_d"] / 2.0,
                                         base_h - pin_bottom + 0.01,
                                         V(bx0 + px, by0 + py, pin_bottom)))

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
        "side": side, "inner": inner, "base_h": base_h, "feet_z": feet_z,
        "pcb_top": pcb_top, "stack_top": stack_top, "pin_bottom": pin_bottom,
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

    print("%s: cube %.1f mm, inner %.1f mm; above the outside bottom: "
          "feet %.1f, PCB top %.1f, stack top %.1f, pin ends %.1f mm; "
          "font %s"
          % (VARIANTS[variant]["name"], info["side"], info["inner"],
             info["feet_z"], info["pcb_top"], info["stack_top"],
             info["pin_bottom"], info["font"]))
    print("written to %s" % outdir)
    print("DONE")

    # Show the result when run inside the FreeCAD GUI
    if App.GuiUp:
        doc = App.newDocument("calib_cube_" + variant)
        doc.addObject("Part::Feature", "Base").Shape = base
        doc.addObject("Part::Feature", "Lid").Shape = lid
        doc.recompute()


main()
