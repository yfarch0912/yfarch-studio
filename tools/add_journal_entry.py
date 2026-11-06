#!/usr/bin/env python3
"""Sisipkan satu entri Jurnal terbaru ke index.html (paling atas daftar).

Pemakaian:
    python3 tools/add_journal_entry.py entry.json

entry.json:
{
  "slug": "notre-dame-de-paris",    // WAJIB: kebab-case unik -> /artikel/<slug>
  "date": "06 NOV 2026",            // tampil di baris jurnal
  "category": "ARSITEKTUR DUNIA",   // label kategori
  "title": "...",
  "read": "3 min read",
  "excerpt": "...",                 // 1-2 kalimat di daftar
  "body": "...",                    // isi modal (teks biasa; akan di-escape)
  "thumb": "assets/journal/2026-11-06-xxx.webp",
  "thumb_alt": "Foto ... (Foto: Nama via Wikimedia Commons, lisensi)",
  "images": [                      // galeri artikel (WAJIB >= 4 untuk edisi baru)
    {"src": "assets/journal/...-foto.webp", "kind": "FOTO ASLI",
     "caption": "... — Nama via Wikimedia Commons (CC BY-SA 4.0)"},
    {"src": "assets/journal/...-ilustrasi-ai.webp", "kind": "ILUSTRASI AI",
     "caption": "Ilustrasi AI: ... — bukan foto"}
  ]
}

Aturan gambar (keputusan user 2026-11-06): fokus visual — setiap artikel baru
WAJIB banyak gambar (>= 4), dokumentasi foto ASLI wajib ada (>= 2, berkredit),
ilustrasi AI boleh dan WAJIB berlabel kind "ILUSTRASI AI".

Yang dilakukan:
1. Semua .journal-row lama: data-note +1 (href baris = /artikel/<slug>, tetap).
2. Baris baru disisipkan tepat setelah <div class="journal-list"> (data-note=0,
   href="/artikel/<slug>").
3. Objek baru di-unshift ke array notesData pada skrip inline.
4. Maksimal MAX_ROWS baris di beranda; sisanya terpotong dari HTML
   (arsip tetap ada di journal/*.md dan riwayat git).
5. Validasi: jumlah baris == jumlah notesData, data-note berurutan 0..n-1.
6. Bangun ulang artikel.html (indeks /artikel) + artikel/<slug>.html per artikel.
"""
import json
import re
import sys

MAX_ROWS = 6
INDEX = "index.html"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def js_str(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ") + "'"


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as f:
        e = json.load(f)
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", e.get("slug", "")), \
        "entry.json WAJIB punya slug kebab-case unik (untuk /artikel/<slug>)"

    with open(INDEX, encoding="utf-8") as f:
        html = f.read()

    # --- 1) naikkan nomor baris lama ---
    # baris ke-i punya data-note="i"; setelah entri baru masuk di index 0, naik 1.
    # (href baris kini /artikel/<slug> milik artikelnya sendiri — tidak berubah.)
    def bump(m: re.Match) -> str:
        return f'class="journal-row" data-note="{int(m.group(1)) + 1}"'

    html, n_bumped = re.subn(
        r'class="journal-row" data-note="(\d+)"', bump, html)

    # --- 2) sisipkan baris baru ---
    row = (
        f'        <a href="/artikel/{e["slug"]}" class="journal-row" data-note="0" data-cursor="lens">\n'
        '          <div class="journal-thumb">\n'
        f'            <img src="{e["thumb"]}" alt="{esc(e["thumb_alt"])}" loading="lazy" />\n'
        '          </div>\n'
        '          <div>\n'
        f'            <div class="journal-meta">{esc(e["date"])} &nbsp;/&nbsp; {esc(e["category"])}</div>\n'
        f'            <h3 class="journal-title">{esc(e["title"])}</h3>\n'
        f'            <span class="journal-read">{esc(e["read"])} &nbsp;→</span>\n'
        '          </div>\n'
        '          <p class="journal-excerpt">\n'
        f'            {esc(e["excerpt"])}\n'
        '          </p>\n'
        '        </a>\n'
    )
    anchor = '<div class="journal-list">\n'
    assert anchor in html, "jangkar .journal-list tidak ditemukan"
    html = html.replace(anchor, anchor + row, 1)

    # --- 3) unshift notesData ---
    images_js = ""
    if e.get("images"):
        items = ",\n".join(
            "            { src: %s, kind: %s, caption: %s }"
            % (js_str(im["src"]), js_str(im["kind"]), js_str(im["caption"]))
            for im in e["images"])
        images_js = ",\n          images: [\n" + items + "\n          ]"
    obj = (
        "        {\n"
        f"          date: {js_str(e['date'] + ' / ' + e['category'])},\n"
        f"          slug: {js_str(e['slug'])},\n"
        f"          title: {js_str(e['title'])},\n"
        f"          body: {js_str(e['body'])}{images_js}\n"
        "        },\n"
    )
    anchor2 = "const notesData = [\n"
    assert anchor2 in html, "jangkar notesData tidak ditemukan"
    html = html.replace(anchor2, anchor2 + obj, 1)

    n_rows_pre = len(re.findall(r'class="journal-row"', html))

    # --- 4) potong kelebihan (tertua = terakhir) ---
    rows = list(re.finditer(
        r'        <a href="/artikel/[^"]+" class="journal-row" data-note="\d+"[\s\S]*?        </a>\n', html))
    if len(rows) > MAX_ROWS:
        last = rows[-1]
        html = html[:last.start()] + html[last.end():]
        # pop objek terakhir notesData: blok "        {\n ... },\n      ];" -> sisakan yang lain
        html = re.sub(
            r"(        \{[^{}]*\},\n)        \{[^{}]*\},\n      \];",
            lambda m: m.group(1) + "      ];", html, count=1) \
            if False else html
        # cara aman: potong objek terakhir notesData dengan pemindai kurung
        # yang sadar string (tahan array images[] bersarang di dalam objek)
        i = html.find("const notesData = [")
        j = html.find("];", i)
        seg = html[i:j]
        starts, depth, in_str, esc_ch = [], 0, False, False
        for k, ch in enumerate(seg):
            if in_str:
                if esc_ch: esc_ch = False
                elif ch == "\\": esc_ch = True
                elif ch == "'": in_str = False
                continue
            if ch == "'": in_str = True
            elif ch == "{":
                if depth == 0: starts.append(k)
                depth += 1
            elif ch == "}": depth -= 1
        assert len(starts) >= 2, "objek notesData < 2 saat pemotongan"
        html = html[:i] + seg[: starts[-1]] + html[j:]

    # --- 5) validasi ---
    n_rows = len(re.findall(r'class="journal-row"', html))
    i = html.find("const notesData = [")
    j = html.find("];", i)
    n_notes = html[i:j].count("date: ")
    notes_idx = [int(x) for x in re.findall(r'class="journal-row" data-note="(\d+)"', html)]
    assert n_rows == n_notes, f"baris ({n_rows}) != notesData ({n_notes})"
    assert notes_idx == list(range(n_rows)), f"data-note tidak berurutan: {notes_idx}"
    assert n_bumped == n_rows_pre - 1, f"bump {n_bumped} != baris lama {n_rows_pre - 1}"

    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK: entri '{e['title'][:60]}' masuk. Baris jurnal sekarang: {n_rows}")

    # --- 6) bangun ulang halaman penuh artikel.html ---
    import os
    import subprocess
    builder = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "build_artikel_page.py")
    r = subprocess.run([sys.executable, builder], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr[:400])
    assert r.returncode == 0, "build_artikel_page.py gagal"
    page = open("artikel.html", encoding="utf-8").read()
    assert e["title"].replace("&", "&amp;") in page or e["title"] in page, \
        "judul entri baru tidak ada di artikel.html"
    import os as _os
    art_path = _os.path.join("artikel", e["slug"] + ".html")
    assert _os.path.exists(art_path), f"halaman artikel/{e['slug']}.html tidak terbuat"
    art = open(art_path, encoding="utf-8").read()
    assert e["title"].replace("&", "&amp;") in art or e["title"] in art, \
        "judul entri baru tidak ada di halaman artikelnya"
    print(f"halaman per-artikel OK: /artikel/{e['slug']}")


if __name__ == "__main__":
    main()
