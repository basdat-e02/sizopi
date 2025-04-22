-- 1. Tabel PENGGUNA
CREATE TABLE PENGGUNA (
  username        VARCHAR(50) PRIMARY KEY,
  email           VARCHAR(100) NOT NULL,
  password        VARCHAR(50)  NOT NULL,
  nama_depan      VARCHAR(50)  NOT NULL,
  nama_tengah     VARCHAR(50),
  nama_belakang   VARCHAR(50)  NOT NULL,
  no_telepon      VARCHAR(15)  NOT NULL
);

-- 2. Tabel PENGUNJUNG
CREATE TABLE PENGUNJUNG (
  username_P      VARCHAR(50) PRIMARY KEY,
  alamat          VARCHAR(200) NOT NULL,
  tgl_lahir       DATE         NOT NULL,
  FOREIGN KEY (username_P) REFERENCES PENGGUNA(username)
);

-- 3. Tabel DOKTER_HEWAN
CREATE TABLE DOKTER_HEWAN (
  username_DH     VARCHAR(50) PRIMARY KEY,
  no_STR          VARCHAR(50) NOT NULL,
  FOREIGN KEY (username_DH) REFERENCES PENGGUNA(username)
);

-- 4. Tabel SPESIALISASI
CREATE TABLE SPESIALISASI (
  username_SH         VARCHAR(50) NOT NULL,
  nama_spesialisasi   VARCHAR(100) NOT NULL,
  PRIMARY KEY (username_SH, nama_spesialisasi),
  FOREIGN KEY (username_SH) REFERENCES DOKTER_HEWAN(username_DH)
);

-- 5. Tabel PENJAGA_HEWAN
CREATE TABLE PENJAGA_HEWAN (
  username_jh    VARCHAR(50) PRIMARY KEY,
  id_staf        UUID         NOT NULL,
  FOREIGN KEY (username_jh) REFERENCES PENGGUNA(username)
);

-- 6. Tabel PELATIH_HEWAN
CREATE TABLE PELATIH_HEWAN (
  username_lh    VARCHAR(50) PRIMARY KEY,
  id_staf        UUID         NOT NULL,
  FOREIGN KEY (username_lh) REFERENCES PENGGUNA(username)
);

-- 7. Tabel STAF_ADMIN
CREATE TABLE STAF_ADMIN (
  username_sa    VARCHAR(50) PRIMARY KEY,
  id_staf        UUID         NOT NULL,
  FOREIGN KEY (username_sa) REFERENCES PENGGUNA(username)
);

-- 8. Tabel HABITAT
CREATE TABLE HABITAT (
  nama           VARCHAR(50) PRIMARY KEY,
  luas_area      DECIMAL     NOT NULL,
  kapasitas      INT         NOT NULL,
  status         VARCHAR(100) NOT NULL
);

-- 9. Tabel HEWAN
CREATE TABLE HEWAN (
  id                     UUID PRIMARY KEY,
  nama                   VARCHAR(100),
  spesies                VARCHAR(100) NOT NULL,
  asal_hewan             VARCHAR(100) NOT NULL,
  tanggal_lahir          DATE,
  status_kesehatan       VARCHAR(50)  NOT NULL,
  nama_habitat           VARCHAR(50),
  url_foto               VARCHAR(255) NOT NULL,
  FOREIGN KEY (nama_habitat) REFERENCES HABITAT(nama)
);

-- 10. Tabel CATATAN_MEDIS
CREATE TABLE CATATAN_MEDIS (
  id_hewan               UUID       NOT NULL,
  username_dh            VARCHAR(50),
  tanggal_pemeriksaan    DATE       NOT NULL,
  diagnosis              VARCHAR(100),
  pengobatan             VARCHAR(100),
  status_kesehatan       VARCHAR(50) NOT NULL,
  catatan_tindak_lanjut  VARCHAR(100),
  PRIMARY KEY (id_hewan, tanggal_pemeriksaan),
  FOREIGN KEY (id_hewan)    REFERENCES HEWAN(id),
  FOREIGN KEY (username_dh) REFERENCES DOKTER_HEWAN(username_DH)
);

-- 11. Tabel PAKAN
CREATE TABLE PAKAN (
  id_hewan    UUID       NOT NULL,
  jadwal      TIMESTAMP  NOT NULL,
  jenis       VARCHAR(50) NOT NULL,
  jumlah      INT         NOT NULL,
  status      VARCHAR(50) NOT NULL,
  PRIMARY KEY (id_hewan, jadwal),
  FOREIGN KEY (id_hewan) REFERENCES HEWAN(id)
);

-- 12. Tabel MEMBERI
CREATE TABLE MEMBERI (
  id_hewan    UUID       PRIMARY KEY,
  jadwal      TIMESTAMP  NOT NULL,
  username_jh VARCHAR(50),
  FOREIGN KEY (id_hewan)    REFERENCES HEWAN(id),
  FOREIGN KEY (username_jh) REFERENCES PENJAGA_HEWAN(username_jh)
);

-- 13. Tabel FASILITAS
CREATE TABLE FASILITAS (
  nama           VARCHAR(50) PRIMARY KEY,
  jadwal         TIMESTAMP  NOT NULL,
  kapasitas_max  INT        NOT NULL
);

-- 14. Tabel ATRAKSI
CREATE TABLE ATRAKSI (
  nama_atraksi  VARCHAR(50) PRIMARY KEY,
  lokasi        VARCHAR(100) NOT NULL,
  FOREIGN KEY (nama_atraksi) REFERENCES FASILITAS(nama)
);

-- 15. Tabel JADWAL_PENUGASAN
CREATE TABLE JADWAL_PENUGASAN (
  username_lh       VARCHAR(50) NOT NULL,
  tgl_penugasan     TIMESTAMP   NOT NULL,
  nama_atraksi      VARCHAR(50),
  PRIMARY KEY (username_lh, tgl_penugasan),
  FOREIGN KEY (username_lh)  REFERENCES PELATIH_HEWAN(username_lh),
  FOREIGN KEY (nama_atraksi) REFERENCES ATRAKSI(nama_atraksi)
);

-- 16. Tabel BERPARTISIPASI
CREATE TABLE BERPARTISIPASI (
  nama_fasilitas  VARCHAR(50) NOT NULL,
  id_hewan        UUID        NOT NULL,
  PRIMARY KEY (nama_fasilitas, id_hewan),
  FOREIGN KEY (nama_fasilitas) REFERENCES FASILITAS(nama),
  FOREIGN KEY (id_hewan)       REFERENCES HEWAN(id)
);

-- 17. Tabel JADWAL_PEMERIKSAAN_KESEHATAN
CREATE TABLE JADWAL_PEMERIKSAAN_KESEHATAN (
  id_hewan                    UUID NOT NULL,
  tgl_pemeriksaan_selanjutnya DATE NOT NULL,
  freq_pemeriksaan_rutin      INT  NOT NULL,
  PRIMARY KEY (id_hewan, tgl_pemeriksaan_selanjutnya),
  FOREIGN KEY (id_hewan) REFERENCES HEWAN(id)
);

-- 18. Tabel WAHANA
CREATE TABLE WAHANA (
  nama_wahana    VARCHAR(50) PRIMARY KEY,
  peraturan      TEXT        NOT NULL
);

-- 19. Tabel ADOPTER
CREATE TABLE ADOPTER (
  username_adopter  VARCHAR(50) UNIQUE,
  id_adopter        UUID        PRIMARY KEY,
  total_kontribusi  INT         NOT NULL,
  FOREIGN KEY (username_adopter) REFERENCES PENGUNJUNG(username_P)
);

-- 20. Tabel INDIVIDU
CREATE TABLE INDIVIDU (
  nik         CHAR(16)    PRIMARY KEY,
  nama        VARCHAR(100) NOT NULL,
  id_adopter  UUID,
  FOREIGN KEY (id_adopter) REFERENCES ADOPTER(id_adopter)
);

-- 21. Tabel ORGANISASI
CREATE TABLE ORGANISASI (
  npp              CHAR(8)     PRIMARY KEY,
  nama_organisasi  VARCHAR(100) NOT NULL,
  id_adopter       UUID,
  FOREIGN KEY (id_adopter) REFERENCES ADOPTER(id_adopter)
);

-- 22. Tabel ADOPSI
CREATE TABLE ADOPSI (
  id_adopter           UUID       NOT NULL,
  id_hewan             UUID       NOT NULL,
  status_pembayaran    VARCHAR(10) NOT NULL,
  tgl_mulai_adopsi     DATE       NOT NULL,
  tgl_berhenti_adopsi  DATE       NOT NULL,
  kontribusi_finansial INT        NOT NULL,
  PRIMARY KEY (id_adopter, id_hewan, tgl_mulai_adopsi),
  FOREIGN KEY (id_adopter) REFERENCES ADOPTER(id_adopter),
  FOREIGN KEY (id_hewan)   REFERENCES HEWAN(id)
);

-- **1. Enable UUID extension**
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- **2. PENGGUNA (95 baris)**
INSERT INTO pengguna(username, email, password, nama_depan, nama_tengah, nama_belakang, no_telepon)
SELECT
  'user' || g                                     AS username,
  'user' || g || '@example.com'                   AS email,
  'pass' || g                                     AS password,
  'NamaDepan' || g                                AS nama_depan,
  CASE WHEN g % 3 = 0 THEN NULL ELSE 'NamaTengah'||g END AS nama_tengah,
  'NamaBelakang' || g                             AS nama_belakang,
  '0812' || LPAD(g::text,8,'0')                   AS no_telepon
FROM generate_series(1,95) AS s(g);

-- **3. PENGUNJUNG (50 baris)**
INSERT INTO pengunjung(username_P, alamat, tgl_lahir)
SELECT
  'user' || g                                   AS username_P,
  'Jl. Contoh No. '||g                          AS alamat,
  (DATE '1980-01-01' + ((g % 40) * INTERVAL '1 year'))::date  AS tgl_lahir
FROM generate_series(1,50) AS s(g);

-- **4. DOKTER_HEWAN (15 baris)**
INSERT INTO dokter_hewan(username_DH, no_STR)
SELECT
  'user' || g                                  AS username_DH,
  'STR-' || LPAD(g::text,5,'0')               AS no_STR
FROM generate_series(1,15) AS s(g);

-- **5. SPESIALISASI (10 baris)**
INSERT INTO spesialisasi(username_SH, nama_spesialisasi)
SELECT
  'user' || g                                 AS username_SH,
  'Spesialisasi_'||g                          AS nama_spesialisasi
FROM generate_series(1,10) AS s(g);

-- **6. PENJAGA_HEWAN (10 baris)**
INSERT INTO penjaga_hewan(username_jh, id_staf)
SELECT
  'user' || (15 + g)                          AS username_jh,
  uuid_generate_v4()                          AS id_staf
FROM generate_series(1,10) AS s(g);

-- **7. PELATIH_HEWAN (10 baris)**
INSERT INTO pelatih_hewan(username_lh, id_staf)
SELECT
  'user' || (25 + g)                          AS username_lh,
  uuid_generate_v4()                          AS id_staf
FROM generate_series(1,10) AS s(g);

-- **8. STAF_ADMIN (10 baris)**
INSERT INTO staf_admin(username_sa, id_staf)
SELECT
  'user' || (35 + g)                          AS username_sa,
  uuid_generate_v4()                          AS id_staf
FROM generate_series(1,10) AS s(g);

-- **9. HABITAT (8 baris)**
INSERT INTO habitat(nama, luas_area, kapasitas, status)
SELECT
  'Habitat_'||g                               AS nama,
  100 + g * 10                                AS luas_area,
  5 + g                                       AS kapasitas,
  CASE WHEN g % 2 = 0 THEN 'Aktif' ELSE 'Perawatan' END AS status
FROM generate_series(1,8) AS s(g);

-- **10. HEWAN (40 baris)**
INSERT INTO hewan(id, nama, spesies, asal_hewan, tanggal_lahir, status_kesehatan, nama_habitat, url_foto)
SELECT
  uuid_generate_v4()                          AS id,
  'Hewan_'||g                                 AS nama,
  'Spesies_'||((g % 5)+1)                     AS spesies,
  'Asal_'||((g % 10)+1)                       AS asal_hewan,
  (DATE '2020-01-01' + (g * INTERVAL '30 day'))::date AS tanggal_lahir,
  CASE WHEN g % 2 = 0 THEN 'Sehat' ELSE 'Perlu Cek' END AS status_kesehatan,
  'Habitat_'||((g % 8)+1)                     AS nama_habitat,
  'https://example.com/foto/'||g||'.jpg'      AS url_foto
FROM generate_series(1,40) AS s(g);

-- **11. CATATAN_MEDIS (10 baris)**
INSERT INTO catatan_medis(id_hewan, username_dh, tanggal_pemeriksaan, diagnosis, pengobatan, status_kesehatan, catatan_tindak_lanjut)
SELECT
  (SELECT id FROM hewan ORDER BY id LIMIT 1 OFFSET (g-1)) AS id_hewan,
  'user'||((g % 15)+1)                                     AS username_dh,
  (CURRENT_DATE - (g * INTERVAL '7 day'))::date           AS tanggal_pemeriksaan,
  'Diagnosis_'||g                                         AS diagnosis,
  'Obat_'||g                                              AS pengobatan,
  CASE WHEN g % 2 = 0 THEN 'Sehat' ELSE 'Perlu Tindakan' END AS status_kesehatan,
  'TindakLanjut_'||g                                     AS catatan_tindak_lanjut
FROM generate_series(1,10) AS s(g);

-- **12. PAKAN (5 baris)**
INSERT INTO pakan(id_hewan, jadwal, jenis, jumlah, status)
SELECT
  (SELECT id FROM hewan ORDER BY id LIMIT 1 OFFSET (g-1)) AS id_hewan,
  NOW() + (g * INTERVAL '1 day')                           AS jadwal,
  'JenisPakan_'||g                                        AS jenis,
  5 + g                                                   AS jumlah,
  CASE WHEN g % 2 = 0 THEN 'Diberi' ELSE 'Pending' END     AS status
FROM generate_series(1,5) AS s(g);

-- **13. MEMBERI (10 baris)**
INSERT INTO memberi(id_hewan, jadwal, username_jh)
SELECT
  (SELECT id FROM hewan ORDER BY id LIMIT 1 OFFSET (g-1))     AS id_hewan,
  NOW() + (g * INTERVAL '2 day')                                AS jadwal,
  'user'||(15 + ((g-1)%10)+1)                                   AS username_jh
FROM generate_series(1,10) AS s(g);

-- **14. FASILITAS (5 baris)**
INSERT INTO fasilitas(nama, jadwal, kapasitas_max)
SELECT
  'Fasilitas_'||g                                          AS nama,
  NOW() + (g * INTERVAL '3 day')                           AS jadwal,
  10 + g                                                   AS kapasitas_max
FROM generate_series(1,5) AS s(g);

-- **15. ATRAKSI (8 baris)**
INSERT INTO atraksi(nama_atraksi, lokasi)
SELECT
  'Atraksi_'||g                                            AS nama_atraksi,
  'Lokasi_'||g                                            AS lokasi
FROM generate_series(1,8) AS s(g);

-- **16. JADWAL_PENUGASAN (10 baris)**
INSERT INTO jadwal_penugasan(username_lh, tgl_penugasan, nama_atraksi)
SELECT
  'user'||(25 + ((g-1)%10)+1)                             AS username_lh,
  NOW() + (g * INTERVAL '4 day')                          AS tgl_penugasan,
  'Atraksi_'||((g % 8)+1)                                 AS nama_atraksi
FROM generate_series(1,10) AS s(g);

-- **17. BERPARTISIPASI (10 baris)**
INSERT INTO berpartisipasi(nama_fasilitas, id_hewan)
SELECT
  'Fasilitas_'||((g % 5)+1)                               AS nama_fasilitas,
  (SELECT id FROM hewan ORDER BY id LIMIT 1 OFFSET (g-1)) AS id_hewan
FROM generate_series(1,10) AS s(g);

-- **18. JADWAL_PEMERIKSAAN_KESEHATAN (10 baris)**
INSERT INTO jadwal_pemeriksaan_kesehatan(id_hewan, tgl_pemeriksaan_selanjutnya, freq_pemeriksaan_rutin)
SELECT
  (SELECT id FROM hewan ORDER BY id LIMIT 1 OFFSET (g-1))        AS id_hewan,
  (CURRENT_DATE + (g * INTERVAL '15 day'))::date                AS tgl_pemeriksaan_selanjutnya,
  (g % 4) + 1                                                   AS freq_pemeriksaan_rutin
FROM generate_series(1,10) AS s(g);

-- **19. WAHANA (5 baris)**
INSERT INTO wahana(nama_wahana, peraturan)
SELECT
  'Wahana_'||g                                                AS nama_wahana,
  'Peraturan untuk Wahana_'||g                               AS peraturan
FROM generate_series(1,5) AS s(g);

-- **20. ADOPTER (20 baris)**
INSERT INTO adopter(username_adopter, id_adopter, total_kontribusi)
SELECT
  'user'||g                                                   AS username_adopter,
  uuid_generate_v4()                                          AS id_adopter,
  (g * 10000)                                                 AS total_kontribusi
FROM generate_series(1,20) AS s(g);

-- **21. INDIVIDU (10 baris)**
INSERT INTO individu(nik, nama, id_adopter)
SELECT
  LPAD((10000+g)::text,16,'0')                                AS nik,
  'NamaIndividu_'||g                                          AS nama,
  (SELECT id_adopter FROM adopter ORDER BY id_adopter LIMIT 1 OFFSET (g-1)) AS id_adopter
FROM generate_series(1,10) AS s(g);

-- **22. ORGANISASI (10 baris)**
INSERT INTO organisasi(npp, nama_organisasi, id_adopter)
SELECT
  LPAD(g::text,8,'0')                                        AS npp,
  'Organisasi_'||g                                           AS nama_organisasi,
  (SELECT id_adopter FROM adopter ORDER BY id_adopter LIMIT 1 OFFSET (10+g-1)) AS id_adopter
FROM generate_series(1,10) AS s(g);

-- **23. ADOPSI (30 baris)**
INSERT INTO adopsi(id_adopter, id_hewan, status_pembayaran, tgl_mulai_adopsi, tgl_berhenti_adopsi, kontribusi_finansial)
SELECT
  (SELECT id_adopter FROM adopter ORDER BY id_adopter LIMIT 1 OFFSET ((g-1)%20))  AS id_adopter,
  (SELECT id FROM hewan       ORDER BY id       LIMIT 1 OFFSET ((g-1)%40))      AS id_hewan,
  CASE WHEN g % 2 = 0 THEN 'Lunas' ELSE 'Pending' END                          AS status_pembayaran,
  (CURRENT_DATE - (g * INTERVAL '30 day'))::date                              AS tgl_mulai_adopsi,
  (CURRENT_DATE - ((g-1) * INTERVAL '15 day'))::date                          AS tgl_berhenti_adopsi,
  (g * 5000)                                                                   AS kontribusi_finansial
FROM generate_series(1,30) AS s(g);
