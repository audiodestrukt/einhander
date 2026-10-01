#!/usr/bin/env python3
"""dsn_freeze_ses.py — build a TAIL-pass DSN: the original DSN + every wire/via of a previous
Freerouting SES as FIXED (wiring), so a second Freerouting run only routes what is still open.

Why: Freerouting's completion is fragile on dense boards — a small geometry change can make one
net silently drop out of the SES while the session still reports success (einhander: QSPI_SCLK
vanished after the C_IN/C_OUT/C_LED pad fix; USB_DP left one pad short). Re-running from scratch
just reshuffles which net fails. The idea: freeze the good 99% and re-route only the remainder.

STATUS: DEAD END with Freerouting 2.2.4 — it stalls after 0-2 passes with even 10 frozen wires
(vias alone are fine), for (type fix|protect|route) alike; v2.4.1 is worse. Kept as a record.

  dsn_freeze_ses.py <in.dsn> <prev.ses> <out.dsn>
  freert224 -de out.dsn -do tail.ses     # tail.ses carries the frozen wires too -> inject with --clear
"""
import re, sys

dsn_in, ses, dsn_out = sys.argv[1:4]
D = open(dsn_in).read()
S = open(ses).read()

# SES coords are integers in um/N for (resolution um N); the DSN body is written in plain um.
m = re.search(r'\(resolution um (\d+)\)', S)
SES_RES = int(m.group(1)) if m else 1
def sc(v): return f'{float(v) / SES_RES:g}'

out, nw, nv = [], 0, 0
net_re = re.compile(r'\(net "?([^"\n]+?)"?\n([\s\S]*?)(?=\n\s*\(net |\n\s*\)\s*\)\s*\)\s*$)')
for nm in net_re.finditer(S):
    net, body = nm.group(1), nm.group(2)
    for w in re.finditer(r'\(path (\S+) (\d+)\s+([-\d\s]+?)\)', body):
        layer, width, pts = w.group(1), w.group(2), w.group(3).split()
        xy = ' '.join(sc(p) for p in pts)
        out.append(f'    (wire (path {layer} {sc(width)} {xy}) (net "{net}") (type fix))')
        nw += 1
    for v in re.finditer(r'\(via "([^"]+)" (-?\d+) (-?\d+)', body):
        out.append(f'    (via "{v.group(1)}" {sc(v.group(2))} {sc(v.group(3))} (net "{net}") (type fix))')
        nv += 1

D = re.sub(r'\n\s*\(wiring[\s\S]*?\n\s{2}\)', '', D)         # drop any prior wiring section
end = D.rstrip().rfind(')')
D = D[:end] + '  (wiring\n' + '\n'.join(out) + '\n  )\n' + D[end:]
open(dsn_out, 'w').write(D)
print(f"dsn_freeze_ses: froze {nw} wires + {nv} vias from {ses} -> {dsn_out}")
