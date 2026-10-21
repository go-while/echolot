#!/usr/bin/env python3
"""nover.py HOST GROUP OUTFILE : read-only OVER dump of a whole group (MODE READER, GROUP, OVER, QUIT only)."""
import socket, sys
host, group, out = sys.argv[1:4]
s = socket.create_connection((host, 119), timeout=120); f = s.makefile('rb')
print(f.readline().strip())
def cmd(c):
    s.sendall(c.encode() + b'\r\n'); return f.readline().decode('latin-1').strip()
print(cmd('MODE READER'))
r = cmd('GROUP ' + group); print(r)
_, n, lo, hi, _ = r.split(None, 4)
r = cmd('OVER %s-%s' % (lo, hi)); print(r)
with open(out, 'wb') as o:
    while True:
        l = f.readline()
        if l in (b'.\r\n', b'.\n', b''):
            break
        o.write(l.rstrip(b'\r\n') + b'\n')
print(cmd('QUIT'))
