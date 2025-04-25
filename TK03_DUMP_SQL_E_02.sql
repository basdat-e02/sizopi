-- init schema -> create_table -> insert_data

-- Membuat schema sizopi
CREATE SCHEMA SIZOPI;

-- search path masuk ke sizopi
SET search_path TO SIZOPI;

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
  peraturan      TEXT        NOT NULL,
  FOREIGN KEY (nama_wahana) REFERENCES FASILITAS(nama)
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

-- Extension for creating uuid
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. PENGGUNA (95 records)
INSERT INTO PENGGUNA (username, email, password, nama_depan, nama_tengah, nama_belakang, no_telepon)
SELECT
  'user' || g AS username,
  'user' || g || '@example.com' AS email,
  'password' || g AS password,
  'Nama' || g AS nama_depan,
  CASE WHEN g % 3 = 0 THEN 'Tengah' || g ELSE NULL END AS nama_tengah,
  'Belakang' || g AS nama_belakang,
  '08' || (1000000 + g)::TEXT AS no_telepon
FROM generate_series(1, 95) AS g;

-- 2. PENGUNJUNG (50 records)
INSERT INTO PENGUNJUNG (username_P, alamat, tgl_lahir)
SELECT
  'user' || g AS username_P,
  'Jl. Contoh No.' || g AS alamat,
  DATE '1990-01-01' + (g || ' days')::interval AS tgl_lahir
FROM generate_series(1, 50) AS g;

-- 3. DOKTER_HEWAN (15 records)
INSERT INTO DOKTER_HEWAN (username_DH, no_STR)
SELECT
  'user' || (g + 50) AS username_DH,
  'STR' || (10000 + g) AS no_STR
FROM generate_series(1, 15) AS g;

-- 4. SPESIALISASI (10 records)
INSERT INTO SPESIALISASI (username_SH, nama_spesialisasi)
SELECT
  'user' || (50 + (g % 15) + 1) AS username_SH,
  CASE (g % 5)
    WHEN 0 THEN 'Mamalia'
    WHEN 1 THEN 'Reptil'
    WHEN 2 THEN 'Unggas'
    WHEN 3 THEN 'Amfibi'
    ELSE 'Ikan'
  END AS nama_spesialisasi
FROM generate_series(1, 10) AS g;

-- 5. PENJAGA_HEWAN (10 records)
INSERT INTO PENJAGA_HEWAN (username_jh, id_staf)
SELECT
  'user' || (g + 65) AS username_jh,
  uuid_generate_v4() AS id_staf
FROM generate_series(1, 10) AS g;

-- 6. PELATIH_HEWAN (10 records)
INSERT INTO PELATIH_HEWAN (username_lh, id_staf)
SELECT
  'user' || (g + 75) AS username_lh,
  uuid_generate_v4() AS id_staf
FROM generate_series(1, 10) AS g;

-- 7. STAF_ADMIN (10 records)
INSERT INTO STAF_ADMIN (username_sa, id_staf)
SELECT
  'user' || (g + 85) AS username_sa,
  uuid_generate_v4() AS id_staf
FROM generate_series(1, 10) AS g;

-- 8. HABITAT (8 records)
INSERT INTO HABITAT (nama, luas_area, kapasitas, status)
SELECT
  CASE g
    WHEN 1 THEN 'Savanna'
    WHEN 2 THEN 'Hutan Hujan'
    WHEN 3 THEN 'Gurun'
    WHEN 4 THEN 'Rawa'
    WHEN 5 THEN 'Tundra'
    WHEN 6 THEN 'Terumbu Karang'
    WHEN 7 THEN 'Pegunungan'
    WHEN 8 THEN 'Padang Rumput'
  END AS nama,
  (500 + g * 100)::DECIMAL AS luas_area,
  (g * 5) AS kapasitas,
  CASE WHEN g % 3 = 0 THEN 'Penuh' ELSE 'Tersedia' END AS status
FROM generate_series(1, 8) AS g;

-- 9. HEWAN (40 records)
INSERT INTO HEWAN (id, nama, spesies, asal_hewan, tanggal_lahir, status_kesehatan, nama_habitat, url_foto)
SELECT
  uuid_generate_v4() AS id,
  'Hewan' || g AS nama,
  CASE (g % 8)
    WHEN 0 THEN 'Singa'
    WHEN 1 THEN 'Gajah'
    WHEN 2 THEN 'Jerapah'
    WHEN 3 THEN 'Harimau'
    WHEN 4 THEN 'Buaya'
    WHEN 5 THEN 'Burung Elang'
    WHEN 6 THEN 'Kodok'
    WHEN 7 THEN 'Ikan Hiu'
  END AS spesies,
  CASE (g % 5)
    WHEN 0 THEN 'Afrika'
    WHEN 1 THEN 'Asia'
    WHEN 2 THEN 'Amerika'
    WHEN 3 THEN 'Australia'
    WHEN 4 THEN 'Eropa'
  END AS asal_hewan,
  DATE '2015-01-01' + (g * 30 || ' days')::interval AS tanggal_lahir,
  CASE (g % 3)
    WHEN 0 THEN 'Sehat'
    WHEN 1 THEN 'Sakit'
    WHEN 2 THEN 'Dalam Pemantauan'
  END AS status_kesehatan,
  (SELECT nama FROM HABITAT ORDER BY nama LIMIT 1 OFFSET (g % 8)) AS nama_habitat,
  'https://example.com/animal/' || g || '.jpg' AS url_foto
FROM generate_series(1, 40) AS g;

-- 10. CATATAN_MEDIS (10 records)
-- Fixed to avoid using g in the subquery
INSERT INTO CATATAN_MEDIS (id_hewan, username_dh, tanggal_pemeriksaan, diagnosis, pengobatan, status_kesehatan, catatan_tindak_lanjut)
WITH 
  hewan_sample AS (SELECT id FROM HEWAN ORDER BY id LIMIT 10),
  doctor_sample AS (SELECT username_DH FROM DOKTER_HEWAN ORDER BY username_DH),
  series AS (SELECT generate_series(1, 10) AS g)
SELECT
  (SELECT id FROM hewan_sample OFFSET ((s.g - 1) % 10) LIMIT 1) AS id_hewan,
  (SELECT username_DH FROM doctor_sample OFFSET ((s.g - 1) % 15) LIMIT 1) AS username_dh,
  DATE '2023-01-01' + (s.g * 15 || ' days')::interval AS tanggal_pemeriksaan,
  'Diagnosis ' || s.g AS diagnosis,
  'Pengobatan ' || s.g AS pengobatan,
  CASE (s.g % 3)
    WHEN 0 THEN 'Membaik'
    WHEN 1 THEN 'Stabil'
    WHEN 2 THEN 'Perlu Pengawasan'
  END AS status_kesehatan,
  'Catatan ' || s.g AS catatan_tindak_lanjut
FROM series s;

-- 11. PAKAN (5 records)
-- Fixed to avoid using g in the subquery
INSERT INTO PAKAN (id_hewan, jadwal, jenis, jumlah, status)
WITH 
  hewan_sample AS (SELECT id FROM HEWAN ORDER BY id LIMIT 5),
  series AS (SELECT generate_series(1, 5) AS g)
SELECT
  (SELECT id FROM hewan_sample OFFSET ((s.g - 1) % 5) LIMIT 1) AS id_hewan,
  TIMESTAMP '2023-03-01 08:00:00' + (s.g || ' hours')::interval AS jadwal,
  CASE (s.g % 3)
    WHEN 0 THEN 'Daging'
    WHEN 1 THEN 'Sayuran'
    WHEN 2 THEN 'Buah'
  END AS jenis,
  (5 * s.g) AS jumlah,
  CASE WHEN s.g % 2 = 0 THEN 'Terjadwal' ELSE 'Selesai' END AS status
FROM series s;

-- 12. MEMBERI (10 records)
-- Fixed to avoid using g in the subquery
INSERT INTO MEMBERI (id_hewan, jadwal, username_jh)
WITH 
  hewan_sample AS (SELECT id FROM HEWAN ORDER BY id LIMIT 10),
  penjaga_sample AS (SELECT username_jh FROM PENJAGA_HEWAN ORDER BY username_jh),
  series AS (SELECT generate_series(1, 10) AS g)
SELECT
  (SELECT id FROM hewan_sample OFFSET ((s.g - 1) % 10) LIMIT 1) AS id_hewan,
  TIMESTAMP '2023-03-01 08:00:00' + (s.g || ' hours')::interval AS jadwal,
  (SELECT username_jh FROM penjaga_sample OFFSET ((s.g - 1) % 10) LIMIT 1) AS username_jh
FROM series s;

-- 13&14. ATRAKSI::FASILITAS (8 records total)
-- First, add all 8 facilities with varied names
INSERT INTO FASILITAS (nama, jadwal, kapasitas_max)
SELECT
  CASE g
    WHEN 1 THEN 'Safari Singa Liar'
    WHEN 2 THEN 'Akrobat Lumba-lumba'
    WHEN 3 THEN 'Penerbangan Elang'
    WHEN 4 THEN 'Parade Gajah Asia'
    WHEN 5 THEN 'Teater Primata Cerdas'
    WHEN 6 THEN 'Momen Penguin Kutub'
    WHEN 7 THEN 'Eksibisi Reptil Langka' 
    WHEN 8 THEN 'Aksi Anjing Laut'
  END AS nama,
  TIMESTAMP '2023-03-01 09:00:00' + (g || ' hours')::interval AS jadwal,
  (50 * g) AS kapasitas_max
FROM generate_series(1, 8) AS g
ON CONFLICT (nama) DO NOTHING;

-- Now insert all 8 attractions at once
INSERT INTO ATRAKSI (nama_atraksi, lokasi)
SELECT
  nama AS nama_atraksi,
  CASE nama
    WHEN 'Safari Singa Liar' THEN 'Arena Savanna'
    WHEN 'Akrobat Lumba-lumba' THEN 'Laguna Biru'
    WHEN 'Penerbangan Elang' THEN 'Dome Langit'
    WHEN 'Parade Gajah Asia' THEN 'Plaza Utama'
    WHEN 'Teater Primata Cerdas' THEN 'Hutan Hujan'
    WHEN 'Momen Penguin Kutub' THEN 'Taman Es'
    WHEN 'Eksibisi Reptil Langka' THEN 'Rumah Kaca Tropis'
    WHEN 'Aksi Anjing Laut' THEN 'Kolam Akuatik'
  END AS lokasi
FROM FASILITAS
LIMIT 8;

-- 15. JADWAL_PENUGASAN (10 records)
-- Fixed to avoid using g in the subquery
INSERT INTO JADWAL_PENUGASAN (username_lh, tgl_penugasan, nama_atraksi)
WITH 
  pelatih_sample AS (SELECT username_lh FROM PELATIH_HEWAN ORDER BY username_lh),
  atraksi_sample AS (SELECT nama_atraksi FROM ATRAKSI ORDER BY nama_atraksi),
  series AS (SELECT generate_series(1, 10) AS g)
SELECT
  (SELECT username_lh FROM pelatih_sample OFFSET ((s.g - 1) % 10) LIMIT 1) AS username_lh,
  TIMESTAMP '2023-03-01 09:00:00' + (s.g || ' days')::interval AS tgl_penugasan,
  (SELECT nama_atraksi FROM atraksi_sample OFFSET ((s.g - 1) % 8) LIMIT 1) AS nama_atraksi
FROM series s;

-- 16. BERPARTISIPASI (10 records)
-- Fixed to avoid using g in the subquery
INSERT INTO BERPARTISIPASI (nama_fasilitas, id_hewan)
WITH 
  hewan_sample AS (SELECT id FROM HEWAN ORDER BY id LIMIT 10),
  fasilitas_sample AS (SELECT nama FROM FASILITAS ORDER BY nama),
  series AS (SELECT generate_series(1, 10) AS g)
SELECT
  (SELECT nama FROM fasilitas_sample OFFSET ((s.g - 1) % 8) LIMIT 1) AS nama_fasilitas,
  (SELECT id FROM hewan_sample OFFSET ((s.g - 1) % 10) LIMIT 1) AS id_hewan
FROM series s;

-- 17. JADWAL_PEMERIKSAAN_KESEHATAN (10 records)
-- Fixed to avoid using g in the subquery
INSERT INTO JADWAL_PEMERIKSAAN_KESEHATAN (id_hewan, tgl_pemeriksaan_selanjutnya, freq_pemeriksaan_rutin)
WITH 
  hewan_sample AS (SELECT id FROM HEWAN ORDER BY id LIMIT 10),
  series AS (SELECT generate_series(1, 10) AS g)
SELECT
  (SELECT id FROM hewan_sample OFFSET ((s.g - 1) % 10) LIMIT 1) AS id_hewan,
  DATE '2023-04-01' + (s.g * 7 || ' days')::interval AS tgl_pemeriksaan_selanjutnya,
  (s.g % 4) + 1 AS freq_pemeriksaan_rutin
FROM series s;

-- 18. WAHANA::FASILITAS (5 records)
-- Now insert records into WAHANA table
INSERT INTO FASILITAS (nama, jadwal, kapasitas_max)
SELECT
  CASE g
    WHEN 1 THEN 'Roller Coaster Safari'
    WHEN 2 THEN 'Gua Kelelawar'
    WHEN 3 THEN 'Perahu Danau'
    WHEN 4 THEN 'Kereta Satwa'
    WHEN 5 THEN 'Taman Bermain Anak'
  END AS nama,
  TIMESTAMP '2023-03-01 09:00:00' + ((g + 8) || ' hours')::interval AS jadwal,
  (60 * g) AS kapasitas_max
FROM generate_series(1, 5) AS g
ON CONFLICT (nama) DO NOTHING;

INSERT INTO WAHANA (nama_wahana, peraturan)
SELECT
  nama AS nama_wahana,
  'Peraturan wahana: ' || nama || '. Dilarang membawa makanan dan minuman. Dilarang berdiri saat wahana beroperasi.' AS peraturan
FROM FASILITAS
WHERE nama IN ('Roller Coaster Safari', 'Gua Kelelawar', 'Perahu Danau', 'Kereta Satwa', 'Taman Bermain Anak')
LIMIT 5;

-- 19. ADOPTER (20 records)
INSERT INTO ADOPTER (username_adopter, id_adopter, total_kontribusi)
SELECT
  CASE WHEN g <= 20 THEN 'user' || g ELSE NULL END AS username_adopter,
  uuid_generate_v4() AS id_adopter,
  (g * 500000) AS total_kontribusi
FROM generate_series(1, 20) AS g;

-- 20. INDIVIDU (10 records)
-- Fixed to avoid using g in the subquery
INSERT INTO INDIVIDU (nik, nama, id_adopter)
WITH 
  adopter_sample AS (SELECT id_adopter FROM ADOPTER ORDER BY id_adopter LIMIT 10),
  series AS (SELECT generate_series(1, 10) AS g)
SELECT
  '1234567890' || LPAD(s.g::TEXT, 6, '0') AS nik,
  'Individu ' || s.g AS nama,
  (SELECT id_adopter FROM adopter_sample OFFSET ((s.g - 1) % 10) LIMIT 1) AS id_adopter
FROM series s;

-- 21. ORGANISASI (10 records)
-- Fixed to avoid using g in the subquery
INSERT INTO ORGANISASI (npp, nama_organisasi, id_adopter)
WITH 
  adopter_sample AS (SELECT id_adopter FROM ADOPTER ORDER BY id_adopter OFFSET 10 LIMIT 10),
  series AS (SELECT generate_series(1, 10) AS g)
SELECT
  '1234' || LPAD(s.g::TEXT, 4, '0') AS npp,
  'Organisasi ' || s.g AS nama_organisasi,
  (SELECT id_adopter FROM adopter_sample OFFSET ((s.g - 1) % 10) LIMIT 1) AS id_adopter
FROM series s;

-- 22. ADOPSI (30 records)
-- Fixed to avoid using g in the subquery
INSERT INTO ADOPSI (id_adopter, id_hewan, status_pembayaran, tgl_mulai_adopsi, tgl_berhenti_adopsi, kontribusi_finansial)
WITH 
  hewan_sample AS (SELECT id FROM HEWAN ORDER BY id LIMIT 30),
  adopter_sample AS (SELECT id_adopter FROM ADOPTER ORDER BY id_adopter LIMIT 20),
  series AS (SELECT generate_series(1, 30) AS g)
SELECT
  (SELECT id_adopter FROM adopter_sample OFFSET ((s.g - 1) % 20) LIMIT 1) AS id_adopter,
  (SELECT id FROM hewan_sample OFFSET ((s.g - 1) % 30) LIMIT 1) AS id_hewan,
  CASE (s.g % 3)
    WHEN 0 THEN 'Lunas'
    WHEN 1 THEN 'Cicilan'
    WHEN 2 THEN 'Pending'
  END AS status_pembayaran,
  DATE '2023-01-01' + (s.g * 5 || ' days')::interval AS tgl_mulai_adopsi,
  DATE '2023-01-01' + ((s.g * 5) + 365 || ' days')::interval AS tgl_berhenti_adopsi,
  (s.g * 100000) AS kontribusi_finansial
FROM series s;
