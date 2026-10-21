import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nntp import NNTP
listfile, outdir = sys.argv[1], sys.argv[2]
delay = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2
nums = [int(x) for x in open(listfile).read().split()]
todo = [x for x in nums if not os.path.exists(f"{outdir}/{x}.txt")]
print("todo", len(todo), flush=True)
def conn():
    n = NNTP(); n.cmd("MODE READER"); n.cmd("GROUP alt.privacy.anon-server"); return n
n = conn(); errs = 0
for i, x in enumerate(todo):
    for attempt in range(5):
        try:
            r = n.cmd(f"ARTICLE {x}")
            if r.startswith("220"):
                data = b"\n".join(n.multi()) + b"\n"
                with open(f"{outdir}/{x}.txt", "wb") as f: f.write(data)
            else:
                print("miss", x, r, flush=True)
            break
        except Exception as e:
            errs += 1
            print("err", x, e, flush=True)
            time.sleep(10 * (attempt + 1))
            try: n = conn()
            except Exception as e2: print("reconn fail", e2, flush=True)
    if i % 200 == 0: print("done", i, flush=True)
    time.sleep(delay)
n.close(); print("finished", flush=True)
