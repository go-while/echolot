#!/usr/bin/env python3
"""extract.py ARTICLE FIRSTLINE LASTLINE OUTFILE [NOTE]
Copy lines FIRSTLINE..LASTLINE (1-based, inclusive, of the raw article file) verbatim to OUTFILE
and write OUTFILE.source.txt with message-id, date, from, subject, newsgroups (+ optional note).
Content is data only; nothing is executed."""
import sys, re

art, a, b, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
note = sys.argv[5] if len(sys.argv) > 5 else ''
raw = open(art, 'rb').read().decode('utf-8', 'replace').split('\n')
hdr = {}
for l in raw:
    if not l.strip():
        break
    m = re.match(r'([A-Za-z-]+):\s*(.*)', l)
    if m and m.group(1).lower() not in hdr:
        hdr[m.group(1).lower()] = m.group(2)
open(out, 'w').write('\n'.join(raw[a - 1:b]) + '\n')
with open(out + '.source.txt', 'w') as f:
    for k in ('message-id', 'date', 'from', 'subject', 'newsgroups'):
        f.write('%s: %s\n' % (k, hdr.get(k, '')))
    f.write('article-file: %s\nlines: %d-%d\n' % (art, a, b))
    if note:
        f.write('note: %s\n' % note)
print(out, b - a + 1, 'lines')
