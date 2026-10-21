import sys, email.utils, email.header
def dec(s):
    try:
        return str(email.header.make_header(email.header.decode_header(s))).replace("\t"," ").replace("\n"," ")
    except Exception: return s
with open(sys.argv[1],encoding='latin-1') as f, open(sys.argv[2],'w',encoding='utf-8') as o:
    o.write("num\tisodate\tsubject\tfrom\tdate\tmsgid\trefs\tbytes\tlines\n")
    for l in f:
        p=l.rstrip("\n").split("\t")
        while len(p)<8: p.append("")
        num,subj,frm,date,mid,refs,by,li=p[:8]
        try: iso=email.utils.parsedate_to_datetime(date).strftime("%Y-%m-%d %H:%M")
        except Exception: iso="?"
        o.write("\t".join([num,iso,dec(subj),dec(frm),date,mid,refs,by,li])+"\n")
