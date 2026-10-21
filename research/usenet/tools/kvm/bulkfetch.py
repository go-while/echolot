"""Read-only bulk fetch of alt.privacy.anon-server articles (ARTICLE only).

Usage: bulkfetch.py FIRST LAST OUTDIR
Stores each article as OUTDIR/<n>.txt (raw bytes, dot-unstuffed).
Never sends POST/IHAVE/AUTHINFO.  Pipelines BATCH requests on one connection.
"""
import os, socket, sys, time

HOST, PORT, GROUP, BATCH = "archive.usenet.blueworldhosting.com", 119, "alt.privacy.anon-server", 20

def connect():
    s = socket.create_connection((HOST, PORT), timeout=120)
    f = s.makefile("rb")
    greet = f.readline()
    if not greet.startswith(b"20"):
        raise RuntimeError(greet)
    s.sendall(f"GROUP {GROUP}\r\n".encode())
    r = f.readline()
    if not r.startswith(b"211"):
        raise RuntimeError(r)
    return s, f

def read_multi(f):
    out = []
    while True:
        l = f.readline()
        if not l:
            raise EOFError
        if l in (b".\r\n", b".\n"):
            return b"".join(out)
        if l.startswith(b".."):
            l = l[1:]
        out.append(l)

def main():
    first, last, outdir = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    todo = [n for n in range(first, last + 1) if not os.path.exists(os.path.join(outdir, f"{n}.txt"))]
    s, f = connect()
    got = missing = 0
    t0 = time.time()
    i = 0
    while i < len(todo):
        batch = todo[i:i + BATCH]
        try:
            s.sendall(b"".join(f"ARTICLE {n}\r\n".encode() for n in batch))
            for n in batch:
                r = f.readline()
                if r.startswith(b"220"):
                    data = read_multi(f)
                    tmp = os.path.join(outdir, f".{n}.tmp")
                    with open(tmp, "wb") as o:
                        o.write(data)
                    os.rename(tmp, os.path.join(outdir, f"{n}.txt"))
                    got += 1
                elif r[:3] in (b"423", b"430"):
                    missing += 1
                else:
                    raise RuntimeError(f"{n}: {r!r}")
            i += BATCH
        except (OSError, EOFError, RuntimeError) as e:
            print("error, reconnecting:", e, flush=True)
            time.sleep(10)
            try:
                s.close()
            except Exception:
                pass
            s, f = connect()
            continue
        if (i // BATCH) % 100 == 0:
            print(f"{i}/{len(todo)} got={got} missing={missing} {time.time()-t0:.0f}s", flush=True)
        time.sleep(0.05)
    s.sendall(b"QUIT\r\n")
    print(f"done got={got} missing={missing} {time.time()-t0:.0f}s", flush=True)

main()
