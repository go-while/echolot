import sys, os, re
d = sys.argv[1]; pat = re.compile(sys.argv[2], re.I | re.M)
ov = {}
for l in open(os.path.join(os.path.dirname(d.rstrip('/')), 'overview.tsv'), encoding='utf-8'):
    p = l.split('\t'); ov[p[0]] = p
for fn in sorted(os.listdir(d), key=lambda x: int(x.split('.')[0])):
    t = open(os.path.join(d, fn), encoding='latin-1').read()
    hits = pat.findall(t)
    if hits:
        n = fn.split('.')[0]; p = ov.get(n, ['']*6)
        print(f"{n}\t{p[1]}\t{len(hits)}\t{p[3][:40]}\t{p[2][:70]}")
