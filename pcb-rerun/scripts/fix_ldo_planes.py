#!/usr/bin/env python3
"""fix_ldo_planes.py — make the LDO corner obey the plane rule.

Freerouting built GND/V3V3 as trace networks on the SIGNAL layers even though this
4-layer board has dedicated inner planes (In1=GND, In2=V3V3). In the LDO cluster that
produced 2 F.Cu shorts (a GND track and a V3V3 track each clipping the wrong C_OUT pad)
and left VBUS dangling. Fix, deterministically:

  1. delete every GND/V3V3 TRACK whose midpoint is in the LDO bbox (they're redundant with
     the planes), plus the dangling VBUS B.Cu stubs there;
  2. drop a fanout via (F.Cu<->B.Cu, through the planes) on each GND/V3V3 pad of C_IN/C_OUT/U3
     so those pads reach their plane directly — no signal-layer copper;
  3. route the ONE net with no plane, VBUS, as a short F.Cu trace from C_IN.1 to the VBUS rail.

Run with pcbnew open on the board (IPC API). Verify after with check_floating.py + kicad-cli drc.
"""
import kipy
from kipy.board_types import Track, Via, BoardLayer
from kipy.geometry import Vector2

# LDO cluster bounding box (mm) — C_IN(108) U3(116) C_OUT(124); excludes J1/R_CC (x<104) and the MCU.
BB = (104.0, 126.0, 127.0, 132.0)            # x0,y0,x1,y1
NM = 1_000_000
VBUS_RAIL = (105.78, 131.08)                 # existing F.Cu VBUS rail endpoint to tie C_IN.1 into
PLANE_OF = {"GND": "In1.Cu", "V3V3": "In2.Cu"}

import time
b = None
for _ in range(20):
    try:
        b = kipy.KiCad().get_board()
        break
    except Exception:
        time.sleep(2)
if b is None:
    raise SystemExit("could not connect to KiCad IPC — is pcbnew open on the board?")
nets = {n.name: n for n in b.get_nets() if n.name}


def inbb(p):
    return BB[0] * NM <= p.x <= BB[2] * NM and BB[1] * NM <= p.y <= BB[3] * NM


def mid(t):
    return Vector2.from_xy((t.start.x + t.end.x) // 2, (t.start.y + t.end.y) // 2)


# 1) delete redundant power tracks + dangling VBUS B.Cu stubs in the cluster
kill = []
for t in b.get_tracks():
    if isinstance(t, Via):
        continue
    net = t.net.name if t.net else ""
    if not inbb(mid(t)):
        continue
    if net in ("GND", "V3V3"):
        kill.append(t)
    elif net == "VBUS" and t.layer == BoardLayer.BL_B_Cu:
        kill.append(t)
if kill:
    b.remove_items(kill)
print(f"deleted {len(kill)} redundant power tracks/stubs in LDO bbox")

# 2) fanout via on each GND/V3V3 pad of the three parts -> straight to its inner plane
want = {"C_IN": {"GND"}, "C_OUT": {"GND", "V3V3"}, "U3": {"GND", "V3V3"}}
new = []
placed = []
for fp in b.get_footprints():
    ref = fp.reference_field.text.value
    if ref not in want:
        continue
    for pd in fp.definition.pads:
        nm = pd.net.name if pd.net else ""
        if nm in want[ref]:
            v = Via()
            v.position = pd.position
            v.diameter = 600_000
            v.drill_diameter = 300_000
            v.net = nets[nm]
            new.append(v)
            placed.append(f"{ref}.{pd.number}->{nm}@{PLANE_OF[nm]}")

# 3) the one plane-less net: VBUS trace C_IN.1 -> VBUS rail
cin1 = None
for fp in b.get_footprints():
    if fp.reference_field.text.value == "C_IN":
        for pd in fp.definition.pads:
            if (pd.net.name if pd.net else "") == "VBUS":
                cin1 = pd.position
if cin1 is not None:
    tr = Track()
    tr.start = cin1
    tr.end = Vector2.from_xy(int(VBUS_RAIL[0] * NM), int(VBUS_RAIL[1] * NM))
    tr.width = 250_000
    tr.layer = BoardLayer.BL_F_Cu
    tr.net = nets["VBUS"]
    new.append(tr)

b.create_items(new)
b.refill_zones()
b.save()
print("added fanout vias:", ", ".join(placed))
print(f"added VBUS trace C_IN.1 -> rail{VBUS_RAIL}")
print("saved. now: python3 scripts/check_floating.py && kicad-cli pcb drc ...")
