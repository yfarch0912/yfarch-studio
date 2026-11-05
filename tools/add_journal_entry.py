#!/usr/bin/env python3
"""Sisipkan satu entri Jurnal terbaru ke index.html (paling atas daftar).

Pemakaian:
    python3 tools/add_journal_entry.py entry.json

entry.json:
{
  "date": "06 NOV 2026",            // tampil di baris jurnal
  "category": "ARSITEKTUR DUNIA",   // label kategori
  "title": "...",
  "read": "3 min read",
  "excerpt": "...",                 // 1-2 kalimat di daftar
  "body": "...",                    // isi modal (teks biasa; akan di-escape)
  "thumb": "assets/journal/2026-11-06-xxx.webp",
  "thumb_alt": "Ilustrasi ..."
}

Yang dilakukan:
1. Semua .journal-row lama: data-note +1, href #note-(n+1).
2. Baris baru disisipkan tepat setelah <div class="journal-list"> (data-note=0).
3. Objek baru di-unshift ke array notesData pada skrip inline.
4. Maksimal MAX_ROWS baris di beranda; sisanya terpotong dari HTML
   (arsip tetap ada di journal/*.md dan riwayat git).
5. Validasi: jumlah baris == jumlah notesData, data-note berurutan 0..n-1.
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

    with open(INDEX, encoding="utf-8") as f:
        html = f.read()

    # --- 1) naikkan nomor baris lama ---
    # pola asli: baris ke-i punya data-note="i" dan href="#note-(i+1)";
    # setelah entri baru masuk di index 0, keduanya naik 1.
    def bump(m: re.Match) -> str:
        return (f'href="#note-{int(m.group(1)) + 1}" class="journal-row" '
                f'data-note="{int(m.group(2)) + 1}"')

    html, n_bumped = re.subn(
        r'href="#note-(\d+)" class="journal-row" data-note="(\d+)"', bump, html)

    # --- 2) sisipkan baris baru ---
    row = (
        '        <a href="#note-1" class="journal-row" data-note="0" data-cursor="lens">\n'
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
    obj = (
        "        {\n"
        f"          date: {js_str(e['date'] + ' / ' + e['category'])},\n"
        f"          title: {js_str(e['title'])},\n"
        f"          body: {js_str(e['body'])}\n"
        "        },\n"
    )
    anchor2 = "const notesData = [\n"
    assert anchor2 in html, "jangkar notesData tidak ditemukan"
    html = html.replace(anchor2, anchor2 + obj, 1)

    # --- 4) potong kelebihan (tertua = terakhir) ---
    rows = list(re.finditer(
        r'        <a href="#note-\d+" class="journal-row" data-note="\d+"[\s\S]*?        </a>\n', html))
    if len(rows) > MAX_ROWS:
        last = rows[-1]
        html = html[:last.start()] + html[last.end():]
        # pop objek terakhir notesData: blok "        {\n ... },\n      ];" -> sisakan yang lain
        html = re.sub(
            r"(        \{[^{}]*\},\n)        \{[^{}]*\},\n      \];",
            lambda m: m.group(1) + "      ];", html, count=1) \
            if False else html
        # cara aman: potong objek terakhir tepat sebelum "];" milik notesData
        i = html.find("const notesData = [")
        j = html.find("];", i)
        seg = html[i:j]
        objs = seg.rstrip()
        assert objs.endswith("},"), "objek terakhir notesData tidak berakhir },"
        seg2 = objs[: objs.rfind("        {")]
        html = html[:i] + seg2 + html[j:]

    # --- 5) validasi ---
    n_rows = len(re.findall(r'class="journal-row"', html))
    i = html.find("const notesData = [")
    j = html.find("];", i)
    n_notes = html[i:j].count("date: ")
    notes_idx = [int(x) for x in re.findall(r'class="journal-row" data-note="(\d+)"', html)]
    assert n_rows == n_notes, f"baris ({n_rows}) != notesData ({n_notes})"
    assert notes_idx == list(range(n_rows)), f"data-note tidak berurutan: {notes_idx}"
    assert n_bumped == n_rows - 1, f"bump {n_bumped} != baris lama {n_rows - 1}"

    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK: entri '{e['title'][:60]}' masuk. Baris jurnal sekarang: {n_rows}")


if __name__ == "__main__":
    main()
