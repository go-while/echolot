#!/usr/bin/env python3
"""Keyword search over parsed subject TSVs (all/*.tsv). Writes subjects.tsv (+score, terms)."""
import re, sys, glob, os, collections

base = sys.argv[1]
CORE = [  # (regex, weight)
    (r'yamn', 10), (r'echolot', 9), (r'pingd', 9), (r'pinger', 7), (r'\bpinging\b', 2),
    (r'mixmaster|\bmixmas', 5), (r'mixmin', 6), (r'remailer', 3), (r'\bremops?\b', 4),
    (r'type[\s-]*(ii|2)\b', 3), (r'\bmlist', 6), (r'pubring', 6), (r'keyring', 3),
    (r'\bsec3\b', 7), (r'\bzax\b', 6), (r'\bcrooks?\b', 1), (r'\bfrell\b', 5),
    (r'virebent', 6), (r'mixfit', 6), (r'omnimix', 6), (r'quicksilver', 4), (r'\bqsl\b', 3),
    (r'\bnyms?\b|nymserv|\bnym[-_ ]?server', 4), (r'conf\.pm', 9), (r'allpingers', 9),
    (r'\bstats?\b.*remail|remail.*\bstats?\b', 2), (r'\bdizum\b', 2), (r'paranoici', 2),
    (r'\bmixes?\b|\bmixnet', 1), (r'\bchain(s|ing)?\b', 1),
]
GENERIC = [(r'\bpatch', 2), (r'\bset ?up\b', 1), (r'\binstall', 1), (r'how ?to\b', 1), (r'tutorial', 1),
           (r'\bconfig', 1)]
FROMRE = [(r'\bzax\b|mixmin\.net', 6), (r'sec3', 7), (r'virebent', 5), (r'\bfrell\b', 4), (r'yamn', 6),
          (r'pinger', 6), (r'echolot', 6), (r'crooks?\b', 3)]
ANONGROUPS = {'alt.privacy.anon-server', 'alt.privacy'}
CORE = [(re.compile(p, re.I), w, p) for p, w in CORE]
GENERIC = [(re.compile(p, re.I), w, p) for p, w in GENERIC]
FROMRE = [(re.compile(p, re.I), w, p) for p, w in FROMRE]
NOISE = re.compile(r'\b(iphone|viagra|cialis|casino|loan|replica|bitcoin doubler)\b', re.I)

out = open(os.path.join(base, 'subjects.tsv'), 'w')
out.write('group\tnumber\tdate\tfrom\tsubject\tmessage-id\tscore\tterms\n')
cnt = collections.Counter()
tot = collections.Counter()
for f in sorted(glob.glob(os.path.join(base, 'all', '*.tsv'))):
    for line in open(f, encoding='utf-8', errors='replace'):
        p = line.rstrip('\n').split('\t')
        if len(p) < 6:
            continue
        g, num, date, frm, subj, mid = p[:6]
        tot[g] += 1
        score = 0
        terms = []
        core_hit = False
        for rx, w, name in CORE:
            if rx.search(subj):
                # weak terms only count if they are not the sole evidence in non-anon groups
                score += w
                terms.append(name)
                if w >= 3:
                    core_hit = True
        for rx, w, name in FROMRE:
            if rx.search(frm):
                score += w
                terms.append('from:' + name)
                core_hit = True
        gen = 0
        for rx, w, name in GENERIC:
            if rx.search(subj):
                gen += w
                terms.append(name)
        if not core_hit:
            # only weak/generic evidence: keep generic only in the anon groups and only if a weak core term too
            if not (g in ANONGROUPS and score > 0 and gen > 0):
                continue
        score += gen
        if NOISE.search(subj):
            score -= 5
        if score <= 0:
            continue
        out.write('\t'.join([g, num, date, frm, subj, mid, str(score), ','.join(terms)]) + '\n')
        cnt[g] += 1
out.close()
for g in sorted(tot):
    print('%-40s rows=%7d matches=%6d' % (g, tot[g], cnt[g]))
print('total rows', sum(tot.values()), 'matches', sum(cnt.values()))
