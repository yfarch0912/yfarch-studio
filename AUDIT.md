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

## Ronde 4 — Routing bersih + artikel per halaman (2026-11-06, perintah user)
- vercel.json cleanUrls: semua URL tanpa .html (/artikel.html → /artikel, /index.html → /).
- Jurnal tidak lagi satu halaman ramai: artikel.html menjadi INDEKS (kartu tautan), setiap artikel berdiri di halaman sendiri artikel/<slug>.html (dibangun tools/build_artikel_page.py dari notesData; bidang slug baru di notesData + entry.json).
- Baris jurnal di beranda kini tautan langsung ke /artikel/<slug> (modal baca openNote dihapus); tombol "Semua artikel" → /artikel.
- Halaman artikel: hero + isi + galeri + navigasi artikel lebih baru/lebih lama; canonical bersih yfarchstudio.web.id/artikel/<slug>.
- Uji: smoke jsdom 11/11; uji ujung-ke-ujung tool di sandbox (entri ke-7: slug wajib, nomor ulang, pemotongan 6 baris, halaman usang terhapus) lulus — termasuk perbaikan validasi bump saat pemotongan.

## Ronde 5 — Kursor invert landing (2026-11-06, perintah user)
- Kursor lama (panah bawaan + titik lime membuntuti + ring putus-putus) diganti kursor invert ala galeri: titik kecil putih mix-blend-mode:difference mengikuti pointer rapat (lerp 0.4); panah bawaan disembunyikan hanya pada pointer halus (html.custom-cursor-on dari JS + media pointer:fine ≥769px; sentuh/HP tetap bawaan).
- Masuk area gambar (data-cursor="lens": showreel, 6 kartu karya, 6 baris artikel): titik memudar dan ring berubah jadi bulatan besar 88px putih difference (invert penuh). Di tautan/tombol: membesar sedang (18px/48px). Di kolom isian: kursor kustom sembunyi, kursor teks bawaan bekerja.
- State kini via delegasi mouseover (tahan konten dinamis/modal/chat). Smoke jsdom 8/8.

## Ronde 6 — Smooth scrolling Lenis + perbaikan modal (2026-11-06, perintah user)
- Mesin gulir lama (hijack roda buatan sendiri) diganti Lenis 1.1.18 (CDN jsdelivr): fisika durasi 1,25 dtk, gulir tetap natif (sticky/parallax/reveal utuh), stop saat modal terbuka, data-lenis-prevent pada kartu modal & panel chat. Cadangan: tanpa CDN / prefers-reduced-motion → gulir bawaan + behavior smooth. Halaman artikel ikut memakai Lenis (snippet di builder).
- PERBAIKAN REGRESI ronde 5: openModal masih memanggil bindCursorTargets() yang sudah dihapus saat kursor diganti delegasi → berpotensi ReferenceError saat modal dibuka. Panggilan basi dibuang; teruji modal karya buka/tutup bersih (smoke 6/6).

## Ronde 7 — Audit menyeluruh + pemulihan routing per halaman (2026-11-10, perintah user)
Temuan audit (live + lokal):
- **KRITIS — routing per halaman putus:** batas 6 baris beranda memotong notesData dan builder MENGHAPUS artikel/<slug>.html milik entri terpotong. 4 artikel arsip studio (mono-pitch, kanopi carport, bata ekspos, denah 4 kamar) live **404**; GEM akan menyusul terhapus pada edisi berikutnya.
- robots.txt & sitemap.xml tidak ada (404); halaman 404 = bawaan Vercel 79 byte polos.
- Halaman artikel tanpa og:image/Twitter Card/JSON-LD; og:image beranda menunjuk domain vercel.app, bukan domain utama.
- Header keamanan minim (hanya HSTS dari Vercel); aset /assets tanpa cache panjang.
- Sehat: semua tautan internal bersih tanpa .html; canonical benar; semua <img> ber-alt; node --check lulus; Lenis & kursor invert utuh. Bobot beranda 1,57 MB (12 gambar data-URI portofolio, karakter berkas tunggal kiriman user — diterima sadar, tidak diubah).

Perbaikan:
- **Routing per halaman dipulihkan permanen:** builder kini menggabungkan notesData + arsip journal/*.json (notesData menang; terurut tanggal desc) → 10 halaman artikel, indeks /artikel memuat semua 10, rantai prev/next melintasi arsip. 4 entri arsip dipulihkan dari riwayat git (commit f580758) ke journal/arsip-<slug>.json; gambar arsip-1..4.webp masih ada. Halaman hanya dihapus bila slug hilang dari gabungan data — edisi harian berikutnya tidak akan memutus URL lama.
- **SEO:** sitemap.xml (12 URL + lastmod) dibangun otomatis oleh builder tiap edisi; robots.txt menunjuk sitemap; og:image + Twitter Card di indeks & semua halaman artikel; JSON-LD schema Article (headline, datePublished, author/publisher) per artikel; og:image beranda → domain yfarchstudio.web.id.
- **404 bermerek:** 404.html seirama halaman artikel (tautan Beranda / Semua artikel / WhatsApp).
- **Header:** vercel.json + X-Content-Type-Options, Referrer-Policy, X-Frame-Options SAMEORIGIN, Permissions-Policy; Cache-Control immutable 1 tahun untuk /assets/* (nama berkas unik bertanggal).
- Uji: builder bersih; node --check lulus; smoke jsdom 10/10 (6 baris beranda, 10 kartu indeks, arsip pulih + canonical + JSON-LD valid + og:image, rantai GEM→arsip, galeri Bosco utuh).

## Ronde 8 — Semua animasi 3D disederhanakan menjadi statis (2026-11-11, perintah user)
Latar: user menilai animasi 3D membuat landing "kurang simple" dan memilih opsi "sederhanakan semua animasi 3D" (bukan hero saja).
- **Hero:** showreel 22 detik (4 mode berganti otomatis, rotasi mengikuti kursor + putaran otomatis, telemetri sudut berubah-ubah) DIHAPUS. Canvas kini satu gambar isometric statis (sudut tetap 0.62/0.36, build 100%, mode Full Isometric + panah struktur). Tab mode (4 tombol), progress bar, tombol "Play with sound" + synth WebAudio, dan baris petunjuk kursor dihapus dari HTML & JS. Canvas digambar ulang hanya saat resize/load/scroll (kotak hero memang melebar saat scroll) agar tetap tajam — gambarnya sendiri tidak bergerak.
- **About dissector:** putaran otomatis + yaw mengikuti kursor dihapus; gambar statis pada explode saat ini. Slider explode & tombol 4 lapis TETAP berfungsi (interaksi sengaja oleh pengunjung, menggambar ulang satu frame per perubahan) — bukan animasi ambient.
- **Services:** Arch statis (sudut tetap); Interior statis (furnitur terakit, explode 0, tanpa hover); Masterplan statis (garis bidik crosshair kursor dihapus); Build statis di tahap akhir 100% (time-lapse otomatis + scrub kursor dihapus; progress bar penuh; readout tahap 5/5).
- **Methodology (hww):** ayunan yaw sinusoidal dihapus; sudut tetap 0.56; tombol 6 fase tetap mengganti tahap gambar secara statis.
- Semua teks "GERAKKAN KURSOR…" diganti keterangan statis yang jujur. Yang TIDAK diubah: kursor invert (ronde 5), Lenis (ronde 6), pelebaran kotak hero saat scroll, reveal scroll & counter statistik — bukan animasi 3D.
- Uji: node --check lulus; smoke jsdom eksekusi penuh (canvas di-stub): 0 error, 7 canvas utuh, 0 tombol mode/sound/progress, 0 teks petunjuk kursor. Berkas menyusut ±7,3 KB.

## Ronde 9 — Canvas isometric diganti video arsitektur (2026-11-11, perintah user)
Klarifikasi user atas ronde 8: maksudnya bukan distatiskan — seluruh isometric 3D diganti **video hasil generate bertema arsitektur**.
- 6 video digenerate (batas alat 6/pesan): hero (orbit rumah tropis mono-pitch, senja), about (kolom beton & kisi kayu), services arch (eksterior modern), int (ruang keluarga hangat), mp (aerial kawasan), build (time-lapse konstruksi). Semua 1280×720 10 dtk; frame tiap video diperiksa visual satu per satu sebelum dipasang. Master mentah (77 MB) disimpan di luar repo (~/yfarch-video-src).
- Web: hero dikompres 2,4 MB (720p CRF30); lima lainnya ±0,5–1,1 MB (540p CRF32); poster WebP per panel. Total video ±6,7 MB; yang di bawah lipatan lazy-load via IntersectionObserver (poster tampil duluan, video diputar saat mendekati viewport, jeda saat jauh; prefers-reduced-motion → poster saja).
- 6 canvas diganti <video> memakai id/class CSS yang sama (layout utuh); mesin JS keenam canvas + slider explode About dihapus; tombol lapis About kini hanya mengganti teks rincian (readout "LAPIS: …"). Semua judul/readout panel ditulis ulang jujur + label "ILUSTRASI VIDEO AI" di keterangan panel (video generik, bukan dokumentasi proyek asli).
- Tersisa 1 canvas: methodology (#hww-bim-canvas) — video ke-7 menyusul pada pesan berikutnya karena batas 6 video per pesan.
- Uji: node --check lulus; smoke jsdom 0 error (termasuk perbaikan guard matchMedia); 6 <video> + 1 canvas utuh.
