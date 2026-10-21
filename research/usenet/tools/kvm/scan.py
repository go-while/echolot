"""Scan fetched articles for yamn pinger material. Usage: scan.py ARTDIR > hits.tsv"""
import os, re, sys
PATTERNS = {
    "pingd.conf": rb"pingd\.conf",
    "echolot-cfg": rb"\b(my_localpart|my_domain|mixhome|operator_address|recipient_delimiter)\b",
    "mixmaster-key": rb"'mixmaster'\s*=>",
    "echolot4yamn": rb"echolot4yamn|sec3pinger",
    "echolot.html": rb"echolot\.html|templates/",
    "Conf.pm": rb"Conf\.pm|parse_mix_key",
    "uuencode": rb"(?m)^begin [0-7]{3} \S",
    "yenc": rb"(?m)^=ybegin ",
    "b64-attach": rb"(?is)Content-Transfer-Encoding:\s*base64.{0,400}?(filename|name)=\"?[^\"\r\n]*\.(zip|pm|conf|cfg|html|tar|gz|tgz|pl|txt)",
    "qsl-src": rb"QSLite-[0-9.]+\.src|QSAam-[0-9.a-z]+\.src|src\.zip",
    "yamn-cfg": rb"(?m)^\s*\[(Mail|Stats|Urls|Files|Remailer)\]\s*$",
    "pinger": rb"(?i)\bpinger\b",
}
COMP = {k: re.compile(v, re.I if k not in ("uuencode", "yenc", "yamn-cfg") else 0) for k, v in PATTERNS.items()}
def hdr(data, name):
    m = re.search(rb"(?mi)^" + name + rb":\s*(.*)$", data.split(b"\n\n", 1)[0] if b"\n\n" in data else data[:4000])
    return m.group(1).strip().decode("latin-1", "replace") if m else ""
for fn in sorted(os.listdir(sys.argv[1]), key=lambda x: int(x.split(".")[0]) if x[0].isdigit() else 0):
    if not fn.endswith(".txt") or not fn[0].isdigit():
        continue
    data = open(os.path.join(sys.argv[1], fn), "rb").read().replace(b"\r\n", b"\n")
    body = data.split(b"\n\n", 1)[1] if b"\n\n" in data else b""
    hits = [k for k, c in COMP.items() if c.search(body if k != "b64-attach" else data)]
    if hits and hits != ["pinger"]:
        print("\t".join([fn[:-4], hdr(data, b"Date")[:31], hdr(data, b"From")[:50], hdr(data, b"Subject")[:80], ",".join(hits), str(len(data))]))
