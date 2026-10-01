#!/usr/bin/python3
"""Routing-quality metrics (needs KiCad's pcbnew -> system python) for a .kicad_pcb: track length/segments per layer, vias, zones."""
import sys, json, collections, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
L = collections.defaultdict(float); S = collections.Counter(); vias = 0; netlen = collections.defaultdict(float)
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T: vias += 1; continue
    mm = t.GetLength() / 1e6; ln = b.GetLayerName(t.GetLayer())
    L[ln] += mm; S[ln] += 1; netlen[t.GetNetname()] += mm
zones = collections.Counter(f"{z.GetNetname()}@{b.GetLayerName(z.GetLayer())}" for z in b.Zones() if not z.GetIsRuleArea())
power = {"GND", "V3V3"}
out = {
  "track_mm_total": round(sum(L.values()), 1),
  "track_mm_by_layer": {k: round(v, 1) for k, v in sorted(L.items())},
  "segments_by_layer": dict(sorted(S.items())),
  "segments_total": sum(S.values()),
  "vias": vias,
  "power_track_mm": round(sum(v for n, v in netlen.items() if n in power), 1),
  "nets_with_tracks": len(netlen),
  "zones": dict(zones),
  "footprints": len(b.GetFootprints()),
}
print(json.dumps(out, indent=1))
