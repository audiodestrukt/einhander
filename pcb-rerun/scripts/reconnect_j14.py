#!/usr/bin/env python3
"""reconnect_j14.py — reconnect J1's SMD ground pad (14) to the GND plane with a fanout via
placed clear of J1's 1.6 mm mounting hole (the earlier via sat 0.04 mm from it — a DFM
hole-spacing danger). Try offsets around the pad, away from every drilled hole, and keep the
first that gives >=0.5 mm hole edge clearance; connect pad->via with a short F.Cu stub."""
import math
import time

import kipy
from kipy.board_types import Track, Via, BoardLayer
from kipy.geometry import Vector2

BOARD = "index.circuit.kicad_pcb"
NM = 1_000_000
VIA_D, VIA_DRILL, TRK_W = 600_000, 300_000, 200_000
MIN_HOLE_EDGE = 0.5 * NM


def parse_holes(path):
    txt = open(path).read()

    def sx(s, i):
        i += 1; out = []
        while True:
            while s[i] in " \t\r\n":
                i += 1
            if s[i] == ")":
                return out, i + 1
            if s[i] == "(":
                v, i = sx(s, i); out.append(v)
            elif s[i] == '"':
                j = i + 1
                while s[j] != '"':
                    if s[j] == "\\":
                        j += 1
                    j += 1
                out.append(s[i + 1:j]); i = j + 1
            else:
                j = i
                while s[j] not in ' \t\r\n()':
                    j += 1
                out.append(s[i:j]); i = j
    root, _ = sx(txt, txt.index("("))
    fa = lambda l, k: [x for x in l if isinstance(x, list) and x and x[0] == k]

    def g(l, k):
        for x in l:
            if isinstance(x, list) and x and x[0] == k:
                return x
    pts = []
    for fp in fa(root, "footprint"):
        at = g(fp, "at"); fx, fy = float(at[1]), float(at[2])
        rot = float(at[3]) if len(at) > 3 else 0.0
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for pad in fa(fp, "pad"):
            if pad[2] not in ("thru_hole", "np_thru_hole"):
                continue
            dr = g(pad, "drill")
            if not dr:
                continue
            d = max(float(dr[2]), float(dr[3])) if dr[1] == "oval" else float(dr[1])
            pat = g(pad, "at"); px, py = float(pat[1]), float(pat[2])
            pts.append(((fx + px * ca - py * sa) * NM, (fy + px * sa + py * ca) * NM, d / 2 * NM))
    for x in root:
        if isinstance(x, list) and x and x[0] == "via":
            at = g(x, "at"); dr = g(x, "drill")
            pts.append((float(at[1]) * NM, float(at[2]) * NM, (float(dr[1]) if dr else 0) / 2 * NM))
    return pts


holes = parse_holes(BOARD)
b = None
for _ in range(20):
    try:
        b = kipy.KiCad().get_board(); break
    except Exception:
        time.sleep(2)
nets = {n.name: n for n in b.get_nets() if n.name}
from kipy.board_types import BoardLayer as BL
CLR = 200_000

# J1.14 pad position
pad = None
for fp in b.get_footprints():
    if fp.reference_field.text.value == "J1":
        for pd in fp.definition.pads:
            if str(pd.number) == "14":
                pad = pd.position
assert pad is not None
px, py = pad.x, pad.y

# remove any prior J1.14 fanout (GND via within 1.5mm of the pad + GND F.Cu stub touching it)
rm = []
for v in b.get_vias():
    if v.net and v.net.name == "GND" and math.hypot(v.position.x - px, v.position.y - py) < 1_500_000:
        rm.append(v)
for t in b.get_tracks():
    if t.net and t.net.name == "GND":
        if math.hypot(t.start.x - px, t.start.y - py) < 60_000 or math.hypot(t.end.x - px, t.end.y - py) < 60_000:
            rm.append(t)
if rm:
    b.remove_items(rm)
    b.refill_zones()
print(f"removed {len(rm)} prior J1.14 fanout item(s)")

# foreign copper (net != GND): tracks + vias + pads
fsegs, fpts = [], []
for t in b.get_tracks():
    if t.net and t.net.name != "GND":
        fsegs.append((t.start.x, t.start.y, t.end.x, t.end.y, t.width / 2))
for v in b.get_vias():
    if v.net and v.net.name != "GND":
        fpts.append((v.position.x, v.position.y, v.diameter / 2))
for fp in b.get_footprints():
    for pd in fp.definition.pads:
        if pd.net and pd.net.name != "GND":
            fpts.append((pd.position.x, pd.position.y, 500_000))


def seg_d(px_, py_, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0.0, min(1.0, ((px_ - x1) * dx + (py_ - y1) * dy) / L2))
    return math.hypot(px_ - (x1 + t * dx), py_ - (y1 + t * dy))


def hole_ok(vx, vy):
    return all(math.hypot(vx - hx, vy - hy) - VIA_D / 2 - hr >= MIN_HOLE_EDGE for hx, hy, hr in holes)


def copper_ok(vx, vy):
    for x, y, r in fpts:
        if math.hypot(vx - x, vy - y) < VIA_D / 2 + r + CLR:
            return False
    for x1, y1, x2, y2, hw in fsegs:
        if seg_d(vx, vy, x1, y1, x2, y2) < VIA_D / 2 + hw + CLR:
            return False
    return True


def stub_ok(x2, y2):
    for x1s, y1s, x2s, y2s, hw in fsegs:
        for sx_, sy_ in ((px, py), (x2, y2), ((px + x2) / 2, (py + y2) / 2)):
            if seg_d(sx_, sy_, x1s, y1s, x2s, y2s) < TRK_W / 2 + hw + CLR:
                return False
    for x, y, r in fpts:
        if seg_d(x, y, px, py, x2, y2) < TRK_W / 2 + r + CLR:
            return False
    return True


# try a fanout via in a clear spot first (relaxed copper clearance to fab min)
CLR = 130_000
chosen = None
for r in (0.6, 0.8, 1.0, 1.2, 1.4):
    for ang in range(0, 360, 10):
        vx = int(px + math.cos(math.radians(ang)) * r * NM)
        vy = int(py + math.sin(math.radians(ang)) * r * NM)
        if hole_ok(vx, vy) and copper_ok(vx, vy) and stub_ok(vx, vy):
            chosen = (vx, vy); break
    if chosen:
        break

made = []
if chosen:
    via = Via(); via.position = Vector2.from_xy(*chosen)
    via.diameter = VIA_D; via.drill_diameter = VIA_DRILL; via.net = nets["GND"]
    tr = Track(); tr.start = pad; tr.end = Vector2.from_xy(*chosen)
    tr.width = TRK_W; tr.layer = BoardLayer.BL_F_Cu; tr.net = nets["GND"]
    made = [via, tr]
    print(f"reconnected J1.14 -> GND via @({chosen[0]/NM:.2f},{chosen[1]/NM:.2f}) + stub")
else:
    # no room for a via: tie J1.14 to J1's grounded thru-hole pad (J1.1) with a short trace
    j11 = None
    for fp in b.get_footprints():
        if fp.reference_field.text.value == "J1":
            for pd in fp.definition.pads:
                if str(pd.number) == "1":
                    j11 = pd.position
    tr = Track(); tr.start = pad; tr.end = j11
    tr.width = TRK_W; tr.layer = BoardLayer.BL_F_Cu; tr.net = nets["GND"]
    made = [tr]
    print(f"no via room; tied J1.14 -> J1.1 (grounded PTH) with a short F.Cu trace")

b.create_items(made)
b.refill_zones(); b.save()
print("saved")
