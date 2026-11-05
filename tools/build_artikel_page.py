#!/usr/bin/env python3
"""Bangun artikel.html (halaman penuh Artikel/Jurnal) dari notesData di index.html.

Sumber data satu-satunya = array notesData pada index.html (diekstrak via node,
di-eval sebagai JS, dibuang sebagai JSON). Halaman yang dihasilkan statis:
semua artikel tampil utuh (isi + galeri dokumentasi/ilustrasi) — baik untuk SEO
dan tetap sinkron setiap kali halaman ini dibangun ulang.

Pemakaian:  python3 tools/build_artikel_page.py
"""
import json
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
    .toc { margin:34px 0 6px; border-top:1px solid var(--border-light); }
    .toc a { display:flex; gap:14px; align-items:baseline; padding:13px 2px; border-bottom:1px solid var(--border-light); text-decoration:none; }
    .toc a:hover .toc-title { text-decoration:underline; }
    .toc-date { font-family:var(--font-mono); font-size:10.5px; letter-spacing:.06em; color:var(--text-secondary); white-space:nowrap; text-transform:uppercase; }
    .toc-title { font-size:15.5px; font-weight:500; letter-spacing:-.01em; }
    article { padding:52px 0 8px; border-bottom:1px solid var(--border-light); }
    .meta { font-family:var(--font-mono); font-size:11px; letter-spacing:.09em; text-transform:uppercase; color:var(--text-secondary); margin-bottom:12px; }
    h2 { font-size:clamp(26px,4.4vw,36px); font-weight:500; letter-spacing:-.025em; line-height:1.15; margin-bottom:20px; }
    figure { margin:0; }
    figure img { width:100%; display:block; border-radius:16px; background:var(--bg-stone); }
    .hero-img { max-height:560px; object-fit:cover; }
    figcaption { font-family:var(--font-mono); font-size:10px; line-height:1.55; letter-spacing:.03em; color:var(--text-secondary); margin-top:8px; text-transform:uppercase; }
    .img-badge { display:inline-block; background:#111; color:#fff; padding:1px 7px; border-radius:99px; margin-right:6px; font-size:9px; letter-spacing:.08em; }
    .article-body { font-size:16.5px; line-height:1.72; color:#2c2c2a; margin-top:22px; }
    .gallery-title { font-family:var(--font-mono); font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--text-secondary); margin:30px 0 12px; }
    .gallery { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
    .gallery img { height:250px; object-fit:cover; }
    .totop { display:inline-block; margin-top:26px; font-family:var(--font-mono); font-size:11px; letter-spacing:.07em; text-transform:uppercase; text-decoration:none; }
    .totop:hover { text-decoration:underline; }
    footer { max-width:920px; margin:0 auto; padding:34px 20px 60px; display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap;
      font-family:var(--font-mono); font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:var(--text-secondary); }
    footer a { text-decoration:none; } footer a:hover { text-decoration:underline; }
    @media (max-width:620px){ .gallery{ grid-template-columns:1fr; } .gallery img{ height:230px; } .toc a{ flex-direction:column; gap:3px; } }
"""

def esc_text(s: str) -> str:
    return s.replace("&", "&amp;") if "&amp;" not in s else s

def fig(img, cls=""):
    return (f'<figure><img class="{cls}" src="{img["src"]}" alt="{img["caption"]}" loading="lazy" />'
            f'<figcaption><span class="img-badge">{img["kind"]}</span>{img["caption"]}</figcaption></figure>')

def main() -> None:
    out = subprocess.run(["node", "-e", NODE_EXTRACT], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("gagal ekstrak notesData: " + out.stderr[:400])
    notes = json.loads(out.stdout)
    assert notes, "notesData kosong"

    toc, articles = [], []
    for idx, n in enumerate(notes):
        num = idx + 1
        toc.append(f'      <a href="#artikel-{num}"><span class="toc-date">{esc_text(n["date"])}</span>'
                   f'<span class="toc-title">{esc_text(n["title"])}</span></a>')
        imgs = n.get("images") or []
        parts = [f'    <article id="artikel-{num}">',
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
        parts.append('      <a class="totop" href="#atas">↑ Kembali ke atas</a>')
        parts.append('    </article>')
        articles.append("\n".join(parts))

    newest = esc_text(notes[0]["date"].split(" / ")[0])
    page = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Artikel/Jurnal Arsitektur Dunia — YFArchitect Studio</title>
  <meta name="description" content="Halaman penuh Artikel/Jurnal Arsitektur Dunia YFArchitect Studio: telaah pakar karya & metode arsitektur dunia dari sumber terverifikasi, dengan galeri dokumentasi foto asli berkredit dan ilustrasi berlabel jujur. Terbit harian dari Probolinggo." />
  <link rel="canonical" href="https://yfarchstudio.web.id/artikel.html" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Artikel/Jurnal Arsitektur Dunia — YFArchitect Studio" />
  <meta property="og:description" content="Telaah pakar arsitektur dunia, terbit harian. Dokumentasi foto asli berkredit + ilustrasi berlabel." />
  <meta property="og:url" content="https://yfarchstudio.web.id/artikel.html" />
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg" />
  <meta name="theme-color" content="#F6F5F0" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>{CSS}  </style>
</head>
<body id="atas">
  <div class="topbar"><div class="topbar-in">
    <a class="backlink" href="index.html">← Beranda Studio</a>
    <span class="brand">YFARCHITECT STUDIO</span>
  </div></div>
  <div class="wrap">
    <p class="kicker">Artikel/Jurnal YFArchitect Studio · Terbit harian · Probolinggo, Jawa Timur</p>
    <h1>Artikel/Jurnal <em>Arsitektur Dunia</em></h1>
    <p class="intro">Telaah pakar atas karya, metode desain, dan teknologi arsitektur dunia — ditulis dari sumber terverifikasi, dengan dokumentasi foto asli berkredit dan ilustrasi yang dilabeli jujur. Fokus kami visual: setiap artikel dibaca lewat gambar dokumentasinya.</p>
    <p class="countline">{len(notes)} artikel · Terakhir diperbarui {newest}</p>
    <nav class="toc">
{chr(10).join(toc)}
    </nav>
{chr(10).join(articles)}
  </div>
  <footer>
    <span>© YFArchitect Studio — Probolinggo</span>
    <a href="index.html">Beranda</a>
    <a href="https://wa.me/6282142424750" target="_blank" rel="noopener">WhatsApp 082142424750</a>
  </footer>
</body>
</html>
"""
    with open("artikel.html", "w", encoding="utf-8") as f:
        f.write(page)
    print(f"artikel.html dibangun: {len(notes)} artikel, {len(page)} byte")

if __name__ == "__main__":
    main()
