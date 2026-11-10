#!/usr/bin/env python3
"""Bangun halaman Artikel/Jurnal dari notesData di index.html.

Menghasilkan (routing bersih tanpa .html, via vercel.json cleanUrls):
- artikel.html          -> indeks /artikel (daftar semua artikel, kartu tautan)
- artikel/<slug>.html   -> satu halaman penuh per artikel (isi + galeri)

Sumber data = array notesData pada index.html (diekstrak via node) DIGABUNG
arsip journal/*.json: entri lama yang terpotong dari beranda (batas 6 baris)
tetap dapat halaman sendiri — routing per halaman tidak boleh putus.
Setiap entri WAJIB punya bidang slug. Halaman artikel/<slug>.html yang slug-nya
tidak ada di gabungan data akan dihapus. Ikut dibangun: sitemap.xml.

Pemakaian:  python3 tools/build_artikel_page.py
"""
import json
import os
import re
import subprocess
import sys

NODE_EXTRACT = r"""
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const i = html.indexOf('const notesData = [');
const j = html.indexOf('];', i);
const nd = eval(html.slice(i + 'const notesData = '.length, j + 1));
process.stdout.write(JSON.stringify(nd));
"""

BASE = "https://yfarchstudio.web.id"

CSS = """
    :root { --bg-warm:#F6F5F0; --bg-white:#FFFFFF; --bg-stone:#EAEAE4; --text-primary:#111111;
      --text-secondary:#767672; --text-muted:#9A9A95; --border-light:#E5E5E0;
      --font-sans:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
      --font-mono:'JetBrains Mono',monospace; --font-serif:'Instrument Serif',Georgia,serif; }
    * { box-sizing:border-box; margin:0; padding:0; }
    body { background:var(--bg-warm); color:var(--text-primary); font-family:var(--font-sans); -webkit-font-smoothing:antialiased; }
    a { color:inherit; }
    .topbar { position:sticky; top:0; z-index:10; background:rgba(246,245,240,.92); backdrop-filter:blur(8px);
      border-bottom:1px solid var(--border-light); }
    .topbar-in { max-width:920px; margin:0 auto; padding:14px 20px; display:flex; justify-content:space-between; align-items:center; }
    .brand { font-family:var(--font-mono); font-size:11px; letter-spacing:.14em; font-weight:600; }
    .backlink { font-family:var(--font-mono); font-size:11px; letter-spacing:.08em; text-transform:uppercase; text-decoration:none; }
    .backlink:hover { text-decoration:underline; }
    .wrap { max-width:920px; margin:0 auto; padding:0 20px 80px; }
    .kicker { font-family:var(--font-mono); font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--text-secondary); margin:44px 0 14px; }
    h1 { font-size:clamp(38px,6.4vw,58px); font-weight:500; letter-spacing:-.03em; line-height:1.04; }
    h1 em { font-family:var(--font-serif); font-style:italic; font-weight:400; }
    .intro { font-size:16.5px; line-height:1.65; color:#3d3d3a; max-width:640px; margin-top:16px; }
    .countline { font-family:var(--font-mono); font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--text-muted); margin-top:18px; }
    .cards { margin:34px 0 6px; border-top:1px solid var(--border-light); }
    .card { display:flex; gap:18px; padding:18px 2px; border-bottom:1px solid var(--border-light); text-decoration:none; align-items:center; }
    .card:hover .card-title { text-decoration:underline; }
    .card img { width:132px; height:96px; object-fit:cover; border-radius:12px; background:var(--bg-stone); flex:none; }
    .card-date { font-family:var(--font-mono); font-size:10.5px; letter-spacing:.06em; color:var(--text-secondary); text-transform:uppercase; margin-bottom:5px; }
    .card-title { font-size:17px; font-weight:500; letter-spacing:-.01em; line-height:1.35; }
    .card-go { font-family:var(--font-mono); font-size:10.5px; letter-spacing:.07em; text-transform:uppercase; color:var(--text-secondary); margin-top:6px; }
    article { padding:46px 0 8px; }
    .meta { font-family:var(--font-mono); font-size:11px; letter-spacing:.09em; text-transform:uppercase; color:var(--text-secondary); margin-bottom:12px; }
    h2 { font-size:clamp(27px,4.6vw,38px); font-weight:500; letter-spacing:-.025em; line-height:1.15; margin-bottom:20px; }
    figure { margin:0; }
    figure img { width:100%; display:block; border-radius:16px; background:var(--bg-stone); }
    .hero-img { max-height:560px; object-fit:cover; }
    figcaption { font-family:var(--font-mono); font-size:10px; line-height:1.55; letter-spacing:.03em; color:var(--text-secondary); margin-top:8px; text-transform:uppercase; }
    .img-badge { display:inline-block; background:#111; color:#fff; padding:1px 7px; border-radius:99px; margin-right:6px; font-size:9px; letter-spacing:.08em; }
    .article-body { font-size:16.5px; line-height:1.72; color:#2c2c2a; margin-top:22px; }
    .gallery-title { font-family:var(--font-mono); font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--text-secondary); margin:30px 0 12px; }
    .gallery { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
    .gallery img { height:250px; object-fit:cover; }
    .prevnext { display:flex; justify-content:space-between; gap:14px; margin-top:44px; padding-top:22px; border-top:1px solid var(--border-light); flex-wrap:wrap; }
    .prevnext a { font-family:var(--font-mono); font-size:11px; letter-spacing:.07em; text-transform:uppercase; text-decoration:none; max-width:46%; }
    .prevnext a:hover { text-decoration:underline; }
    footer { max-width:920px; margin:0 auto; padding:34px 20px 60px; display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap;
      font-family:var(--font-mono); font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:var(--text-secondary); }
    footer a { text-decoration:none; } footer a:hover { text-decoration:underline; }
    @media (max-width:620px){ .gallery{ grid-template-columns:1fr; } .gallery img{ height:230px; } .card img{ width:104px; height:80px; } }
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />')


def esc_text(s: str) -> str:
    return s if "&amp;" in s else s.replace("&", "&amp;")


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60].rstrip("-")


def abs_src(src: str) -> str:
    return src if src.startswith("/") else "/" + src


def fig(img, cls=""):
    return (f'<figure><img class="{cls}" src="{abs_src(img["src"])}" alt="{img["caption"]}" loading="lazy" />'
            f'<figcaption><span class="img-badge">{img["kind"]}</span>{img["caption"]}</figcaption></figure>')


MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
          "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}


def iso_date(display_date: str) -> str:
    """'10 NOV 2026 / ARSITEKTUR DUNIA' -> '2026-11-10' ('' bila tak terparse)."""
    m = re.match(r"(\d{1,2})\s+([A-Z]{3})\s+(\d{4})", (display_date or "").strip())
    if not m or m.group(2) not in MONTHS:
        return ""
    return f"{m.group(3)}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"


def load_archives(seen_slugs):
    """Entri lama dari journal/*.json yang sudah tidak ada di notesData beranda
    (terpotong batas 6 baris) TETAP harus punya halaman /artikel/<slug> —
    routing per halaman tidak boleh putus. notesData selalu menang."""
    import glob
    extra = []
    for path in sorted(glob.glob("journal/*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                e = json.load(f)
        except Exception:
            continue
        slug = e.get("slug")
        if not slug or slug in seen_slugs or not e.get("title") or not e.get("body"):
            continue
        seen_slugs.add(slug)
        date = e.get("date", "")
        if " / " not in date and e.get("category"):
            date = date + " / " + e["category"]
        extra.append({"date": date, "slug": slug, "title": e["title"],
                      "body": e["body"], "images": e.get("images") or []})
    return extra


def head(title, desc, canonical, og_image="", jsonld=""):
    og_img = ""
    if og_image:
        og_img = (f'\n  <meta property="og:image" content="{og_image}" />'
                  f'\n  <meta name="twitter:card" content="summary_large_image" />'
                  f'\n  <meta name="twitter:title" content="{title}" />'
                  f'\n  <meta name="twitter:description" content="{desc}" />'
                  f'\n  <meta name="twitter:image" content="{og_image}" />')
    ld = f'\n  <script type="application/ld+json">{jsonld}</script>' if jsonld else ""
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{canonical}" />{og_img}
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
  <meta name="theme-color" content="#F6F5F0" />{ld}
  {FONTS}
  <style>{CSS}  </style>
</head>"""

LENIS_SNIPPET = """
  <script src="https://cdn.jsdelivr.net/npm/lenis@1.1.18/dist/lenis.min.js"></script>
  <script>
    (function () {
      if (!window.Lenis) return;
      if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      var lenis = new Lenis({ duration: 1.2, smoothWheel: true });
      function raf(t) { lenis.raf(t); requestAnimationFrame(raf); }
      requestAnimationFrame(raf);
      document.querySelectorAll('a[href^="#"]').forEach(function (a) {
        a.addEventListener('click', function (e) {
          var sel = a.getAttribute('href');
          var target = sel && sel.length > 1 ? document.querySelector(sel) : null;
          if (target) { e.preventDefault(); lenis.scrollTo(target); }
        });
      });
    })();
  </script>
"""

def footer():
    return """  <footer>
    <span>© YFArchitect Studio — Probolinggo</span>
    <a href="/">Beranda</a>
    <a href="/artikel">Semua artikel</a>
    <a href="https://wa.me/6282142424750" target="_blank" rel="noopener">WhatsApp 082142424750</a>
  </footer>""" + LENIS_SNIPPET + """
</body>
</html>
"""


def build_index(notes):
    cards = []
    for n in notes:
        imgs = n.get("images") or []
        thumb = (f'<img src="{abs_src(imgs[0]["src"])}" alt="{imgs[0]["caption"]}" loading="lazy" />'
                 if imgs else "")
        cards.append(
            f'      <a class="card" href="/artikel/{n["slug"]}">{thumb}<span>'
            f'<span class="card-date">{esc_text(n["date"])}</span>'
            f'<span class="card-title">{esc_text(n["title"])}</span>'
            f'<span class="card-go">Baca artikel →</span></span></a>')
    newest = esc_text(notes[0]["date"].split(" / ")[0])
    first_imgs = notes[0].get("images") or []
    og0 = BASE + abs_src(first_imgs[0]["src"]) if first_imgs else ""
    page = head("Artikel/Jurnal Arsitektur Dunia — YFArchitect Studio",
                "Indeks Artikel/Jurnal Arsitektur Dunia YFArchitect Studio: telaah pakar karya & metode arsitektur dunia dari sumber terverifikasi, dengan dokumentasi foto asli berkredit dan ilustrasi berlabel jujur. Setiap artikel berdiri di halaman sendiri. Terbit harian dari Probolinggo.",
                BASE + "/artikel", og0) + f"""
<body id="atas">
  <div class="topbar"><div class="topbar-in">
    <a class="backlink" href="/">← Beranda Studio</a>
    <span class="brand">YFARCHITECT STUDIO</span>
  </div></div>
  <div class="wrap">
    <p class="kicker">Artikel/Jurnal YFArchitect Studio · Terbit harian · Probolinggo, Jawa Timur</p>
    <h1>Artikel/Jurnal <em>Arsitektur Dunia</em></h1>
    <p class="intro">Telaah pakar atas karya, metode desain, dan teknologi arsitektur dunia — ditulis dari sumber terverifikasi, dengan dokumentasi foto asli berkredit dan ilustrasi yang dilabeli jujur. Setiap artikel berdiri di halaman sendiri; pilih satu untuk membaca lengkap dengan galerinya.</p>
    <p class="countline">{len(notes)} artikel · Terakhir diperbarui {newest}</p>
    <nav class="cards">
{chr(10).join(cards)}
    </nav>
  </div>
""" + footer()
    with open("artikel.html", "w", encoding="utf-8") as f:
        f.write(page)
    return len(page)


def build_article(notes, idx):
    n = notes[idx]
    imgs = n.get("images") or []
    og_img = BASE + abs_src(imgs[0]["src"]) if imgs else ""
    iso = iso_date(n["date"])
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": n["title"].replace("&amp;", "&"),
        "datePublished": iso,
        "image": [og_img] if og_img else [],
        "author": {"@type": "Organization", "name": "YFArchitect Studio",
                   "url": BASE + "/"},
        "publisher": {"@type": "Organization", "name": "YFArchitect Studio",
                      "url": BASE + "/"},
        "mainEntityOfPage": f'{BASE}/artikel/{n["slug"]}',
        "inLanguage": "id",
    }, ensure_ascii=False)
    parts = [head(f'{esc_text(n["title"])} — Artikel/Jurnal YFArchitect Studio',
                  "Telaah pakar Artikel/Jurnal Arsitektur Dunia YFArchitect Studio: " + esc_text(n["title"]),
                  f'{BASE}/artikel/{n["slug"]}', og_img, jsonld),
             """
<body id="atas">
  <div class="topbar"><div class="topbar-in">
    <a class="backlink" href="/artikel">← Semua artikel</a>
    <span class="brand">YFARCHITECT STUDIO</span>
  </div></div>
  <div class="wrap">
    <article>
""",
             f'      <div class="meta">Artikel/Jurnal Arsitektur Dunia · {esc_text(n["date"])}</div>',
             f'      <h2>{esc_text(n["title"])}</h2>']
    if imgs:
        parts.append("      " + fig(imgs[0], "hero-img"))
    parts.append(f'      <div class="article-body">{n["body"]}</div>')
    if len(imgs) > 1:
        parts.append('      <div class="gallery-title">Galeri dokumentasi &amp; ilustrasi</div>')
        parts.append('      <div class="gallery">')
        for im in imgs[1:]:
            parts.append("        " + fig(im))
        parts.append('      </div>')
    nav = ['      <nav class="prevnext">']
    if idx > 0:
        nav.append(f'        <a href="/artikel/{notes[idx-1]["slug"]}">← Lebih baru: {esc_text(notes[idx-1]["title"])[:52]}…</a>')
    else:
        nav.append('        <span></span>')
    if idx < len(notes) - 1:
        nav.append(f'        <a href="/artikel/{notes[idx+1]["slug"]}">Lebih lama: {esc_text(notes[idx+1]["title"])[:52]}… →</a>')
    nav.append('      </nav>')
    parts.append("\n".join(nav))
    parts.append('    </article>\n  </div>\n' + footer())
    path = os.path.join("artikel", n["slug"] + ".html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(parts))
    return path


def main() -> None:
    out = subprocess.run(["node", "-e", NODE_EXTRACT], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("gagal ekstrak notesData: " + out.stderr[:400])
    notes = json.loads(out.stdout)
    assert notes, "notesData kosong"
    for n in notes:
        n["slug"] = n.get("slug") or slugify(n["title"])
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", n["slug"]), f"slug tidak valid: {n['slug']}"
    # Gabung arsip lama (routing per halaman tidak boleh putus walau baris
    # beranda dibatasi 6), lalu urutkan semua dari terbaru ke terlama.
    seen = {n["slug"] for n in notes}
    notes = notes + load_archives(seen)
    notes.sort(key=lambda n: iso_date(n["date"]) or "0000-00-00", reverse=True)
    size = build_index(notes)
    os.makedirs("artikel", exist_ok=True)
    made = set()
    for k in range(len(notes)):
        made.add(notes[k]["slug"] + ".html")
        build_article(notes, k)
    for old in os.listdir("artikel"):
        if old.endswith(".html") and old not in made:
            os.remove(os.path.join("artikel", old))
            print("halaman usang dihapus:", old)
    # sitemap.xml: beranda + indeks + satu URL per artikel (routing per halaman)
    urls = [(BASE + "/", iso_date(notes[0]["date"])),
            (BASE + "/artikel", iso_date(notes[0]["date"]))]
    urls += [(f'{BASE}/artikel/{n["slug"]}', iso_date(n["date"])) for n in notes]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in urls:
        sm.append("  <url>")
        sm.append(f"    <loc>{loc}</loc>")
        if lastmod:
            sm.append(f"    <lastmod>{lastmod}</lastmod>")
        sm.append("  </url>")
    sm.append("</urlset>")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(sm) + "\n")
    print(f"sitemap.xml: {len(urls)} URL")
    print(f"artikel.html (indeks) {size} byte + {len(made)} halaman artikel: "
          + ", ".join(sorted(made)))


if __name__ == "__main__":
    main()
