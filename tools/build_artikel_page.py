#!/usr/bin/env python3
"""Bangun halaman Artikel/Jurnal dari notesData di index.html.

Menghasilkan (routing bersih tanpa .html, via vercel.json cleanUrls):
- artikel.html          -> indeks /artikel (daftar semua artikel, kartu tautan)
- artikel/<slug>.html   -> satu halaman penuh per artikel (isi + galeri)

Sumber data satu-satunya = array notesData pada index.html (diekstrak via node).
Setiap entri WAJIB punya bidang slug. Halaman artikel/<slug>.html yang slug-nya
sudah tidak ada di notesData akan dihapus.

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


def head(title, desc, canonical):
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
  <meta property="og:url" content="{canonical}" />
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
  <meta name="theme-color" content="#F6F5F0" />
  {FONTS}
  <style>{CSS}  </style>
</head>"""


def footer():
    return """  <footer>
    <span>© YFArchitect Studio — Probolinggo</span>
    <a href="/">Beranda</a>
    <a href="/artikel">Semua artikel</a>
    <a href="https://wa.me/6282142424750" target="_blank" rel="noopener">WhatsApp 082142424750</a>
  </footer>
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
    page = head("Artikel/Jurnal Arsitektur Dunia — YFArchitect Studio",
                "Indeks Artikel/Jurnal Arsitektur Dunia YFArchitect Studio: telaah pakar karya & metode arsitektur dunia dari sumber terverifikasi, dengan dokumentasi foto asli berkredit dan ilustrasi berlabel jujur. Setiap artikel berdiri di halaman sendiri. Terbit harian dari Probolinggo.",
                BASE + "/artikel") + f"""
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
    parts = [head(f'{esc_text(n["title"])} — Artikel/Jurnal YFArchitect Studio',
                  "Telaah pakar Artikel/Jurnal Arsitektur Dunia YFArchitect Studio: " + esc_text(n["title"]),
                  f'{BASE}/artikel/{n["slug"]}'),
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
    print(f"artikel.html (indeks) {size} byte + {len(made)} halaman artikel: "
          + ", ".join(sorted(made)))


if __name__ == "__main__":
    main()
