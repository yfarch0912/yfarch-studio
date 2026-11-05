# Audit & Perbaikan Situs — YFArchitect Studio

## Ronde 1 (2026-11-06, sebelum jurnal harian)
Sehat: berkas mandiri 1,64 MB, `lang="id"`, alt gambar lengkap, 1 h1, nomor WA konsisten.
Temuan: tanpa meta description/OG/favicon; form Book a Call palsu; chat "AI" = skrip lokal; sosmed hanya toast; tombol All entries statis; klaim "65%" tanpa sumber di excerpt jurnal.

## Ronde 2 (2026-11-06) — SEMUA DIPERBAIKI & DIUJI
Katalog interaksi dummy yang ditemukan (semua dari pembacaan handler JS):
1. `book-call-form` submit → hanya toast konfirmasi palsu, data hilang.
2. `all-projects-btn` → toast "6 of 24 works" (klaim 24 karya; yang ada 6).
3. `all-entries-btn` → toast statis "All 4…" (angka basi begitu jurnal bertambah).
4. `footer-directions-btn` → toast alamat, tidak membuka peta.
5. `.social-link` (IG/Threads) → toast, tidak membuka profil.

Perbaikan yang diterapkan:
- **Head/SEO:** meta description, canonical `https://yfarchstudio.web.id/`, Open Graph + Twitter Card (gambar = foto jurnal), theme-color, favicon SVG monogram YF (`assets/favicon.svg`), JSON-LD ProfessionalService (nama, telepon, alamat Probolinggo, jam, sameAs IG/Threads).
- **Form Book a Call → WhatsApp asli:** submit menyusun pesan (nama+lokasi, jadwal slot terpilih, nomor, kebutuhan) dan membuka `wa.me/6282142424750` dengan teks terisi. Tidak ada lagi konfirmasi palsu.
- **Semua Edisi fungsional:** tombol membuka modal daftar seluruh edisi dari `notesData`; klik edisi membuka isinya (fungsi `openNote` dipakai bersama baris jurnal & daftar edisi). Judul modal catatan kini berlabel "JURNAL ARSITEKTUR DUNIA · <tanggal>".
- **All Projects jujur:** modal berisi tepat 6 karya yang memang tampil di halaman, tanpa angka karangan; klik karya menggulir ke seksi Work.
- **Directions → Google Maps** (query Probolinggo, Jawa Timur).
- **Sosmed → profil asli:** Instagram `https://www.instagram.com/yfarch`, Threads `https://www.threads.net/@yf_arch` (sesuai handle yang tercantum di situs), target _blank + rel noopener.
- **Label asisten jujur:** "AI Architect Assistant / ONLINE" diganti "YFA Asisten Studio — asisten virtual, jawaban otomatis dari data studio" (mesinnya memang skrip kata kunci lokal).
- **Identitas jurnal dipertegas:** judul seksi "Latest notes" → **"Jurnal Arsitektur Dunia"** + masthead mono: "JURNAL YFARCHITECT STUDIO · TERBIT HARIAN · Telaah pakar … · Sumber terverifikasi, foto asli berkredit"; tombol "All entries" → "Semua edisi"; label nav/footer "Journal" → "Jurnal".
- **Klaim dibersihkan:** angka "65%" tanpa sumber dihapus dari excerpt; asterisk markdown liar (`*clerestory*`, `*cross-ventilation*`) dibersihkan.
- **Jurnal edisi perdana ditulis ulang metode pakar + FOTO ASLI:** thumbnail ilustrasi AI diganti foto asli fasad GEM (Fatima Ayman via Wikimedia Commons, CC0, dikreditkan di alt, isi, dan arsip). Isi kini berstruktur ilmiah: OBJEK & KONTEKS → METODE 1 Geometri Kontekstual → METODE 2 Fasad Cahaya Pasif → METODE 3 Sirkulasi sebagai Narasi → Relevansi Praktik Tropis → Sumber & Foto.

Uji: `node --check` skrip inline lulus; smoke jsdom **9/9 PASS** (modal jurnal+struktur+kredit, daftar 5 edisi & navigasinya, link IG asli, form→wa.me berisi data, modal karya 6 tanpa klaim 24).

Catatan sisa (jujur): berkas tetap 1,65 MB (16 gambar data-URI bawaan desain awal) — pemisahan aset bisa menurunkan bobot, tetapi mengubah karakter berkas tunggal kiriman user; belum dilakukan. Slot jadwal konsultasi masih label hari statis (Kam/Jum/Sen/Sel) bawaan desain; tanggal dinamis belum dipasang.

## Ronde 3 — Artikel/Jurnal + halaman penuh + galeri dokumentasi (2026-11-06, perintah user)
- Nama diganti "Jurnal" → "Artikel/Jurnal" di seluruh situs (nav, judul seksi, masthead, meta/OG/JSON-LD, modal, footer).
- Halaman penuh baru: artikel.html (dibangun tools/build_artikel_page.py dari notesData) — semua artikel tampil utuh + galeri; tombol beranda "Semua artikel" kini menaut ke sana (modal daftar edisi dihapus).
- Fokus visual (aturan user): setiap artikel bergaleri banyak gambar; dokumentasi foto ASLI wajib ada & berkredit; ilustrasi AI boleh dengan label "ILUSTRASI AI". Edisi GEM kini 4 gambar: 3 foto asli Wikimedia Commons (Fatima Ayman CC0; Holger Uwe Schmitt CC BY-SA 4.0; Slyronit CC BY-SA 4.0) + 1 ilustrasi AI aksonometrik berlabel.
- Thumbnail 4 entri arsip lama diekstrak dari data-URI menjadi berkas assets/journal/arsip-1..4.webp (kind "DOKUMENTASI STUDIO"); index.html menyusut ±105KB.
- tools/add_journal_entry.py: mendukung field images[], pemotong objek tahan kurung bersarang, dan membangun ulang artikel.html setiap entri baru.
