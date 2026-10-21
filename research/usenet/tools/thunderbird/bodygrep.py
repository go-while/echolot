#!/usr/bin/env python3
"""bodygrep.py DIR > hits.tsv : per article: file, date, from, newsgroups, subject, term counts (body only, quotes excluded)."""
import os, re, sys

TERMS = [('yamn', r'yamn'), ('echolot', r'echolot'), ('pingd', r'pingd'), ('pinger', r'pinger'),
         ('confpm', r'conf\.pm'), ('yamncfg', r'yamn\.cfg'), ('echolothtml', r'echolot\.html'),
         ('e4y', r'echolot4yamn|echolot.?for.?yamn'), ('mlist2', r'mlist2'), ('pubringmix', r'pubring\.mix'),
         ('allpingers', r'allpingers'), ('sec3', r'sec3'), ('diff', r'(?m)^(\+\+\+ |--- a/|@@ -|diff -)'),
         ('perlcfg', r"(?m)^\s*'[a-z_]+'\s*=>"), ('template', r'<TMPL_|\{\{|\$[A-Z_]{4,}\$'),
         ('install', r'install|setup|set up|how ?to|compil')]
RX = [(n, re.compile(p, re.I)) for n, p in TERMS]
d = sys.argv[1]
print('file\tdate\tfrom\tnewsgroups\tsubject\t' + '\t'.join(n for n, _ in TERMS))
for fn in sorted(os.listdir(d)):
    if not fn.endswith('.txt'):
        continue
    t = open(os.path.join(d, fn), 'rb').read().decode('utf-8', 'replace')
    h, _, body = t.partition('\n\n')
    hd = {}
    for l in h.split('\n'):
        m = re.match(r'([A-Za-z-]+):\s*(.*)', l)
        if m and m.group(1).lower() not in hd:
            hd[m.group(1).lower()] = m.group(2)
    body = '\n'.join(l for l in body.split('\n') if not l.lstrip().startswith('>'))
    c = [len(r.findall(body)) for _, r in RX]
    if sum(c[:-1]) == 0:
        continue
    print('\t'.join([fn, hd.get('date', '')[:31], hd.get('from', '')[:60], hd.get('newsgroups', '')[:80],
                     hd.get('subject', '')[:100].replace('\t', ' ')] + [str(x) for x in c]))
