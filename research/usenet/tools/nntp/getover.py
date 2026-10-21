import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nntp import NNTP

OUT = sys.argv[1]
lo, hi = int(sys.argv[2]), int(sys.argv[3])
CH = 5000
n = NNTP()
n.cmd("MODE READER")
print(n.cmd("GROUP alt.privacy.anon-server"), flush=True)
done = 0
if os.path.exists(OUT):
    with open(OUT, encoding="latin-1") as f:
        for l in f:
            done = max(done, int(l.split("\t", 1)[0]))
start = max(lo, done + 1)
with open(OUT, "a", encoding="latin-1") as out:
    a = start
    while a <= hi:
        b = min(a + CH - 1, hi)
        for attempt in range(5):
            try:
                r = n.cmd(f"OVER {a}-{b}")
                if r.startswith("224"):
                    lines = n.multi()
                elif r.startswith("423"):
                    lines = []
                else:
                    raise RuntimeError(r)
                break
            except Exception as e:
                print("err", e, flush=True)
                time.sleep(5 * (attempt + 1))
                n = NNTP(); n.cmd("MODE READER"); n.cmd("GROUP alt.privacy.anon-server")
        for l in lines:
            fs = l.decode("latin-1").split("\t")
            fs = [x.replace("\t", " ") for x in fs[:8]]
            out.write("\t".join(fs) + "\n")
        out.flush()
        print(a, b, len(lines), flush=True)
        a = b + 1
        time.sleep(0.5)
n.close()
