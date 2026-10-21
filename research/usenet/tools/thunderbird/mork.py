#!/usr/bin/env python3
"""Minimal Mork (.msf) reader for Thunderbird news summary files (stdlib only).

Usage: python3 -I mork.py <file.msf> [group]   -> TSV rows to stdout:
  group, artnum, date(UTC ISO), from, subject(with "Re: " if flagged), message-id, references
"""
import re, sys, datetime, email.header

TOK = re.compile(r'''
 (?P<ws>\s+)
|(?P<comment>//[^\n]*)
|(?P<gstart>@\$\$\{[0-9A-Fa-f]+\{@)
|(?P<gend>@\$\$\}[0-9A-Fa-f~]+\}@)
|(?P<cell>\(\s*(?P<col>\^[0-9A-Fa-f]+|[^=^()\s]+)\s*(?:=(?P<val>(?:[^)\\]|\\[\s\S])*)|\^\s*(?P<ref>[0-9A-Fa-f]+(?::[\^0-9A-Za-z]+)?)\s*)\))
|(?P<dopen><)|(?P<dclose>>)
|(?P<topen>\{-?(?P<tid>[0-9A-Fa-f]+(?::\^?[0-9A-Za-z]+)?))
|(?P<mopen>\{)
|(?P<tclose>\})
|(?P<ropen>\[(?P<rcut>-)?(?P<rid>[0-9A-Fa-f]+(?::\^?[0-9A-Za-z]+)?))
|(?P<rclose>\])
|(?P<bare>-?[0-9A-Fa-f]+(?::\^?[0-9A-Za-z]+)?)
|(?P<other>[\s\S])
''', re.X)

ESC = re.compile(r'\\\r?\n|\\([\s\S])|\$([0-9A-Fa-f]{2})')


def _unesc(m):
    if m.group(1) is not None:
        return m.group(1)
    if m.group(2) is not None:
        return chr(int(m.group(2), 16))
    return ''


def decode(v):
    s = ESC.sub(_unesc, v)
    b = s.encode('latin-1', 'replace')
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('latin-1')


def split_id(tid, default_scope):
    if ':' in tid:
        i, sc = tid.split(':', 1)
        return i.upper(), sc.lstrip('^').upper()
    return tid.upper(), default_scope


def parse(text):
    cols = {}      # id -> column name
    atoms = {}     # id -> value
    rows = {}      # (scope,id) -> {colname: value-or-('ref',id)}
    dict_depth = 0
    dict_ns = ['v']
    meta_depth = 0
    table_scope = []   # stack of table scopes
    cur_row = None
    stats = {'other': 0}
    for m in TOK.finditer(text):
        k = m.lastgroup
        if k in ('ws', 'comment', 'gstart', 'gend'):
            continue
        if k == 'cell':
            if cur_row is None and dict_depth == 0:
                continue  # table meta etc.
            col = m.group('col')
            val = m.group('val')
            ref = m.group('ref')
            if dict_depth >= 2:          # meta dict, e.g. (a=c)
                if col == 'a' and val is not None:
                    dict_ns[-1] = val
                continue
            if dict_depth == 1 and cur_row is None:
                if val is None:
                    continue
                if dict_ns[-1] == 'c':
                    cols[col.upper()] = decode(val)
                else:
                    atoms[col.upper()] = decode(val)
                continue
            if cur_row is not None and meta_depth == 0:
                if col.startswith('^'):
                    cname = ('#', col[1:].upper())
                else:
                    cname = col
                if val is not None:
                    cur_row[cname] = decode(val)
                else:
                    cur_row[cname] = ('ref', ref.split(':')[0].upper())
            continue
        if k == 'dopen':
            dict_depth += 1
            if dict_depth == 1:
                dict_ns = ['v']
            continue
        if k == 'dclose':
            if dict_depth > 0:
                dict_depth -= 1
            continue
        if k == 'topen':
            i, sc = split_id(m.group('tid'), 'NONE')
            table_scope.append(sc)
            continue
        if k == 'mopen':
            meta_depth += 1
            continue
        if k == 'tclose':
            if meta_depth:
                meta_depth -= 1
            elif table_scope:
                table_scope.pop()
            continue
        if k == 'ropen':
            sc0 = table_scope[-1] if table_scope else 'NONE'
            i, sc = split_id(m.group('rid'), sc0)
            key = (sc, i)
            if m.group('rcut') or key not in rows:
                rows[key] = {}
            cur_row = rows[key]
            continue
        if k == 'rclose':
            cur_row = None
            continue
        if k == 'other':
            stats['other'] += 1
    return cols, atoms, rows, stats


def resolve(cols, atoms, row):
    out = {}
    for c, v in row.items():
        name = cols.get(c[1], '?' + c[1]) if isinstance(c, tuple) else c
        if isinstance(v, tuple):
            v = atoms.get(v[1], '')
        out[name] = v
    return out


def hdr(s):
    if '=?' in s:
        try:
            return str(email.header.make_header(email.header.decode_header(s)))
        except Exception:
            return s
    return s


def main():
    path = sys.argv[1]
    group = sys.argv[2] if len(sys.argv) > 2 else path.rsplit('/', 1)[-1].rsplit('.msf', 1)[0]
    text = open(path, 'rb').read().decode('latin-1')
    cols, atoms, rows, stats = parse(text)
    n = 0
    w = sys.stdout.write
    for (sc, rid), row in rows.items():
        r = resolve(cols, atoms, row)
        mid = r.get('message-id')
        if not mid:
            continue
        try:
            d = int(r.get('date', '0') or '0', 16)
            ds = datetime.datetime.fromtimestamp(d, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')
        except ValueError:
            ds = '?'
        try:
            flags = int(r.get('flags', '0') or '0', 16)
        except ValueError:
            flags = 0
        subj = hdr(r.get('subject', ''))
        if flags & 0x10:
            subj = 'Re: ' + subj
        fields = [group, str(int(rid, 16)), ds, hdr(r.get('sender', '')), subj, '<' + mid.strip('<>') + '>', r.get('references', '')]
        w('\t'.join(f.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ') for f in fields) + '\n')
        n += 1
    sys.stderr.write('%s: rows=%d msgs=%d cols=%d atoms=%d other=%d\n' % (group, len(rows), n, len(cols), len(atoms), stats['other']))


if __name__ == '__main__':
    main()
