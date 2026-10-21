#!/usr/bin/env python3
"""Read-only NNTP fetcher (raw sockets, stdlib). Only sends: MODE READER, CAPABILITIES, GROUP, ARTICLE, QUIT.

  nfetch.py caps HOST
  nfetch.py ids HOST IDFILE OUTDIR          # one message-id per line -> OUTDIR/<sanitized-id>.txt
  nfetch.py range HOST GROUP FIRST LAST OUTDIR   # ARTICLE <n> -> OUTDIR/<n>.txt
Articles are saved as plain text (dot-unstuffed). Missing ones are logged to OUTDIR/missing.txt.
"""
import socket, sys, os, re, time

BATCH = 20
PAUSE = 0.2


class NNTP:
    def __init__(self, host, port=119):
        self.s = socket.create_connection((host, port), timeout=60)
        self.f = self.s.makefile('rb')
        self.greeting = self.line()

    def line(self):
        l = self.f.readline()
        if not l:
            raise EOFError('connection closed')
        return l.rstrip(b'\r\n').decode('latin-1')

    def send(self, cmd):
        assert cmd.split()[0].upper() in ('MODE', 'CAPABILITIES', 'GROUP', 'ARTICLE', 'BODY', 'HEAD', 'QUIT')
        self.s.sendall(cmd.encode('latin-1') + b'\r\n')

    def multiline(self):
        out = []
        while True:
            l = self.f.readline()
            if not l:
                raise EOFError('closed in multiline')
            l = l.rstrip(b'\r\n')
            if l == b'.':
                break
            if l.startswith(b'..'):
                l = l[1:]
            out.append(l)
        return b'\n'.join(out) + b'\n'

    def cmd(self, c):
        self.send(c)
        return self.line()


def safe(mid):
    return re.sub(r'[^A-Za-z0-9._@-]', '_', mid.strip('<>'))[:180]


def fetch_batch(n, keys, mk, outdir, missing):
    for k in keys:
        n.send('ARTICLE ' + mk(k))
    got = 0
    for k in keys:
        resp = n.line()
        if resp.startswith('220'):
            data = n.multiline()
            with open(os.path.join(outdir, (safe(k) if k.startswith('<') else k) + '.txt'), 'wb') as fh:
                fh.write(data)
            got += 1
        else:
            missing.write('%s\t%s\n' % (k, resp))
    return got


def main():
    mode, host = sys.argv[1], sys.argv[2]
    n = NNTP(host)
    print('greeting:', n.greeting, flush=True)
    if mode == 'caps':
        r = n.cmd('CAPABILITIES')
        print(r)
        if r.startswith('101'):
            print(n.multiline().decode('latin-1'))
        print(n.cmd('MODE READER'))
        for g in ('alt.privacy.anon-server', 'alt.privacy'):
            print(g, n.cmd('GROUP ' + g))
        n.send('QUIT')
        return
    print('mode reader:', n.cmd('MODE READER'), flush=True)
    if mode == 'ids':
        ids = [l.strip() for l in open(sys.argv[3]) if l.strip().startswith('<')]
        outdir = sys.argv[4]
        mk = lambda k: k
    else:
        group, first, last, outdir = sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
        print('group:', n.cmd('GROUP ' + group), flush=True)
        ids = [str(i) for i in range(first, last + 1)]
        mk = lambda k: k
    os.makedirs(outdir, exist_ok=True)
    done = set(os.listdir(outdir))
    ids = [k for k in ids if ((safe(k) if k.startswith('<') else k) + '.txt') not in done]
    missing = open(os.path.join(outdir, 'missing.txt'), 'a')
    total = 0
    for i in range(0, len(ids), BATCH):
        total += fetch_batch(n, ids[i:i + BATCH], mk, outdir, missing)
        missing.flush()
        if (i // BATCH) % 25 == 0:
            print('progress', i + BATCH, '/', len(ids), 'got', total, flush=True)
        time.sleep(PAUSE)
    n.send('QUIT')
    print('done got', total, 'of', len(ids), flush=True)


if __name__ == '__main__':
    main()
