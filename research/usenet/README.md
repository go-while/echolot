# Usenet research: yamn pinger history

Material gathered on 2026-10-21 while recovering how Echolot was made to work
with yamn. The original yamn pinger files are lost:
- SEC3's "echolot4yamn" bundle;
- its `pingd.conf` and YAMN `templates/echolot.html`;
- `yamn.cfg`.

Their only public homes, sec3.net and github.com/sec3pinger, are gone, and the
Wayback Machine, Software Heritage, Common Crawl, archive.today and the Go
module proxy don't have them.

Everything here is public Usenet posts or public web pages, kept with their
Message-IDs or URLs so they can be checked and fetched again.

## What was searched

1. **alt.privacy.anon-server, 2016-01 to 2026-10.** All 59,771 articles
   (numbers 278981–338767), fetched read-only from
   `archive.usenet.blueworldhosting.com:119` and grepped for pinger, Echolot,
   config and patch keywords.
   - The hits are in `hits/apas-2016-2026-body-hits.tsv`.
   - The 36 most useful articles are in `articles/`.
2. **The user's Thunderbird subject indexes.** 36 `.msf` files, 1.8 million
   rows: alt.privacy.anon-server, alt.privacy, alt.free.*, news.admin.*,
   news.software.* and more.
   - 110,540 subject matches, in `hits/subject-matches.tsv.xz`.
   - Matching articles were fetched by Message-ID: about 21,000, plus all of
     alt.privacy.anon-server 2014–15, plus 55 from
     alt.privacy.anon-server.stats (`hits/apas-stats-subjects.tsv.xz`).
   - The 2,207 articles with body hits are in `fetched-articles.tar.xz`.
3. **Wayback Machine captures of SEC3's tutorial** "Install Echolot For YAMN
   Pinger on a VPS", in `wayback/`.

## What was found

- **The yamn patch for Echolot** (`found/Conf.pm.yamn.patch`):
  - Zax (Steve Crook) posted it on 2019-06-02, Message-ID
    `<slrnqf7417.u39.admin@fleegle.mixmin.net>`, "Re: Cloaked Yamn Pinger is
    broken". The patch is dated 2016-02-10.
  - It only changes the key-block regexes in `parse_mix_key`.
  - It is commit `6001207` on the `yamn` branch of this repository.
- **Zax's pinger client config** (`found/yamn.cfg.zax-pinger-client-2019`), in
  `<slrnqf7mgl.u39.admin@fleegle.mixmin.net>`:
  - a sendmail pipe;
  - `UseExpired = true`;
  - `Fetch = false`;
  - the pubring in Echolot's mixhome.
- **Zax's "=" padding patch** for Mixmaster 4096-bit keys ("Re: Attn elvis",
  2016-08-06, `articles/283986.txt`). Not needed for yamn.
- **SEC3's complete `pingd.conf`** for allpingers.net, a Mixmaster-era pinger
  ("Re: Pinger problem", 2016-03-08, `articles/280950.txt`).
- **SEC3's note on GnuPG 2** (2020-12-03, `articles/312322.txt`): use
  crooks/echolot `090a595`.
- **SEC3's tutorial**, in `wayback/`:
  - **2020 version:** stock crooks/echolot, plus Zax's `Conf.pm`, a YAMN
    `echolot.html` and SEC3's `pingd.conf` and `yamn.cfg`.
  - **2021 version:** the same, bundled as `echolot4yamn.zip`.
  - The bundled files themselves were never archived.
- **The YAMN `echolot.html` template, rendered:** Frell's live pinger page
  http://echolot.theremailer.net/yamn/echolot.html
  (`found/2026-10-21_frell-yamn-pinger_echolot.html.rendered.html`). The
  Type I (Cypherpunk) sections are commented out. That is enough to rebuild
  the template against the stock `templates/echolot.html`.
- **Early yamn material from Zax (2014–2015):** announcements, `yamn.cfg`
  examples, and notes on running a pinger (a dedicated Mixmaster or yamn copy
  for the pinger; pinger whitelists on middlemen; the drop to ~50% return
  during key rollover). See `found/2014-*` and `found/2015-*`.
- **Pinger history:**
  - Mixmaster-era pingers: SEC3, allpingers.net, austria, deuxpi, apricot and
    others.
  - yamn pingers: mixmin, Frell (since 2016, posting "Frelled Yamn Stats" to
    alt.privacy.anon-server.stats), Victor, Tincture (closed 2024-10), Haph
    (closed 2025-06), Barnish and Dirge (gone by 2026-10).
- **Still lost:** a yamn-specific `pingd.conf`, the YAMN `echolot.html`
  template file itself, and echolot4yamn.

Each file in `found/` has a `.source.txt` with its Message-ID or URL, date,
author and subject.

## Layout

| Path | Contents |
|---|---|
| `found/` | extracted patches, configs, templates and notes (plain text) |
| `articles/` | 36 full alt.privacy.anon-server articles, by article number |
| `fetched-articles.tar.xz` | 2,207 fetched articles with body hits: `apas2014/`, `byid/`, `stats/` |
| `hits/` | hit lists: body hits 2016–2026 (TSV), subject matches and .stats subjects (TSV, xz) |
| `wayback/` | SEC3's tutorial as captured on 2020-09-20 and 2021-04-08 |
| `tools/thunderbird/` | Mork (`.msf`) parser, subject search, NNTP fetch by Message-ID or OVER, extraction |
| `tools/nntp/` | read-only NNTP client, overview fetch and grep used for the first search |
| `tools/kvm/` | the bulk article fetcher and scanner run on a host close to the news server |

All tools are read-only NNTP clients (no POST, IHAVE or AUTHINFO) and use only
the Python standard library (`python3 -I`).

## Full downloads (not in git)

The complete fetched sets are too big for git. They can be downloaded from
https://pugleaf.net/research/echolot-pinger-usenet-archive/usenet-archive/ (a
copy is also kept on the test host mbox-mo1.pugleaf.net in
`/srv/usenet-archive/`):

| File | Size | SHA-256 |
|---|---|---|
| `apas-2016-2026-articles-278981-338767.tar.xz` | 23 MB | `fd032b6cfad432d0c0e8227c5c299266885464c2c8783bbd956fe234fe822bd8` |
| `tbsearch-2026-10-21.tar.xz` (subject search: 34,556 files) | 13 MB | `de41bcee063db6d48e50c03141a25f672c353110a57fd6b304791398fc5c6483` |

Check them with `sha256sum -c SHA256SUMS` after downloading. They can also be
fetched again by article number or Message-ID from
`archive.usenet.blueworldhosting.com` (full archive) or `news-ams.pugleaf.net`
(the last year only).

## Open leads

- **Ask the Frell and Victor pinger operators** for their `pingd.conf` and
  `templates/echolot.html`. Frell has run its yamn pinger since 2016, so its
  setup is probably the most complete.
- **Rebuild a YAMN `echolot.html`** from Frell's rendered page and add it under
  `contrib/yamn/`. The pages of the test pinger (pugleaf-test) still show the
  empty Cypherpunk sections.
- **Weak keyword matches** in alt.privacy.anon-server before 2014, and the
  bodies of alt.privacy.anon-server.stats beyond 55 articles, were not
  searched.
