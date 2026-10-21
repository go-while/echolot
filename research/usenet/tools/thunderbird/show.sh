#!/bin/sh
# show.sh FILE... : print key headers + body, without PGP signature blocks and quoted lines (if Q=1 keep quotes)
for f in "$@"; do echo "=================== $f"; awk -v q="${Q:-0}" -v max="${MAX:-200}" 'BEGIN{h=1}
 h&&/^(From|Date|Subject|Message-ID|Newsgroups):/{print;next} h&&/^$/{h=0;print;next} h{next}
 /^-----BEGIN PGP SIGNATURE/{s=1} s&&/^-----END PGP SIGNATURE/{s=0;next} s{next}
 /^(Hash|Version|Comment): /{next} /^-----BEGIN PGP SIGNED/{next}
 q==0 && /^ *>/{next} {if(++n<=max)print}' "$f"; done
