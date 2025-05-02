-- DATETIME VS TIMESTAMP

-- 1. Tabel PENGGUNA
CREATE TABLE PENGGUNA (
  username        VARCHAR(50) PRIMARY KEY,
  email           VARCHAR(100) NOT NULL UNIQUE,
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

-- 9.1 Tabel RIWAYAT SATWA : Terbuat ketika update hewan ter update (trigger)
CREATE TABLE RIWAYAT_SATWA (
    id_riwayat      BIGSERIAL PRIMARY KEY,
    id_hewan        UUID        NOT NULL REFERENCES HEWAN(id) ON DELETE CASCADE,
    kolom_diubah    VARCHAR(30) NOT NULL,     -- 'status_kesehatan' atau 'nama_habitat'
    sebelum         VARCHAR(100),
    sesudah         VARCHAR(100),
    dicatat_pada    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
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
  id_hewan    UUID        NOT NULL,
  jadwal      DATETIME    NOT NULL,
  jenis       VARCHAR(50) NOT NULL,
  jumlah      INT         NOT NULL,
  status      VARCHAR(50) NOT NULL,
  PRIMARY KEY (id_hewan, jadwal),
  FOREIGN KEY (id_hewan) REFERENCES HEWAN(id)
);

-- 12. Tabel MEMBERI
CREATE TABLE MEMBERI (
  id_hewan    UUID       PRIMARY KEY,
  jadwal      DATETIME,
  username_jh VARCHAR(50),
  FOREIGN KEY (id_hewan)    REFERENCES PAKAN(id_hewan),
  FOREIGN KEY (jadwal)    REFERENCES PAKAN(jadwal),
  FOREIGN KEY (username_jh) REFERENCES PENJAGA_HEWAN(username_jh)
);

-- 13. Tabel FASILITAS
CREATE TABLE FASILITAS (
  nama           VARCHAR(50) PRIMARY KEY,
  jadwal         DATETIME  NOT NULL,
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
  tgl_penugasan     DATETIME   NOT NULL,
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
  freq_pemeriksaan_rutin      INT  NOT NULL DEFAULT 3,
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

-- 23. Table RESERVASI
CREATE TABLE RESERVASI (
    username_p VARCHAR(50),
    nama_fasilitas VARCHAR(50),
    tanggal_kunjungan DATE,
    jumlah_tiket INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    PRIMARY KEY (username_p, nama_fasilitas, tanggal_kunjungan),
    FOREIGN KEY (username_p) REFERENCES PENGUNJUNG(username_p),
    FOREIGN KEY (nama_fasilitas) REFERENCES FASILITAS(nama)
);

