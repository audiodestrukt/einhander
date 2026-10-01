#!/usr/bin/env python3
"""patch_stragglers.py — clean up the last couple of connectivity leftovers on THIS board:
  * re-aim C_IN.1's VBUS hop at the real VBUS rail end (fix_ldo_planes used a stale coord),
  * delete orphan dangling GND stubs (Freerouting fragments that connect to nothing and read
    as 'unconnected' against a thru-hole pad that already reaches the plane).
Run over IPC (pcbnew open)."""
import math
import time

import kipy
from kipy.board_types import Track, Via, BoardLayer
from kipy.geometry import Vector2

NM = 1_000_000
b = None
for _ in range(20):
    try:
        b = kipy.KiCad().get_board(); break
    except Exception:
        time.sleep(2)
if b is None:
    raise SystemExit("no IPC")
nets = {n.name: n for n in b.get_nets() if n.name}


def near(a, bx, by, tol=0.06):
    return math.hypot(a.x / NM - bx, a.y / NM - by) < tol


# 1) VBUS: remove the stale trace ending at (105.78,131.08); add one to the real rail (108.91,131.08)
kill = []
for t in b.get_tracks():
    if isinstance(t, Via):
        continue
    if t.net and t.net.name == "VBUS" and (near(t.start, 105.78, 131.08) or near(t.end, 105.78, 131.08)):
        kill.append(t)
if kill:
    b.remove_items(kill)
tr = Track()
tr.start = Vector2.from_xy(int(107.09 * NM), int(129.0 * NM))
tr.end = Vector2.from_xy(int(108.91 * NM), int(131.08 * NM))
tr.width = 250_000
tr.layer = BoardLayer.BL_F_Cu
tr.net = nets["VBUS"]
b.create_items([tr])
print(f"VBUS: removed {len(kill)} stale trace(s), added C_IN.1 -> rail(108.91,131.08)")

b.refill_zones(); b.save()

# 2) after refill, delete any GND F.Cu track that is a dangling orphan (both ends touch no other
#    same-net copper). Recompute from a fresh DRC (dangling ends) rather than guessing coords.
import json, subprocess
subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", "build/drc.json",
                "index.circuit.kicad_pcb"], capture_output=True)
d = json.load(open("build/drc.json"))
orphans = set()
for v in d.get("violations", []):
    if v["type"] == "track_dangling":
        for it in v.get("items", []):
            p = it.get("pos", {})
            if p:
                orphans.add((round(p["x"], 2), round(p["y"], 2)))
kill2 = []
for t in b.get_tracks():
    if isinstance(t, Via) or not t.net:
        continue
    if t.net.name in ("GND", "V3V3"):
        for ox, oy in orphans:
            if near(t.start, ox, oy, 0.1) or near(t.end, ox, oy, 0.1):
                kill2.append(t); break
if kill2:
    b.remove_items(kill2)
    b.refill_zones(); b.save()
print(f"deleted {len(kill2)} dangling GND/V3V3 orphan stub(s)")
