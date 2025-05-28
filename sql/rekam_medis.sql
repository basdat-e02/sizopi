-- ========================================
-- 1. INSERT Rekam Medis (CATATAN_MEDIS)
-- ========================================

CREATE OR REPLACE FUNCTION insert_catatan_medis(
    p_id_hewan UUID,
    p_username_dh VARCHAR(50),
    p_tanggal_pemeriksaan DATE,
    p_diagnosis VARCHAR(100),
    p_pengobatan VARCHAR(100),
    p_status_kesehatan VARCHAR(50),
    p_catatan_tindak_lanjut VARCHAR(100)
) RETURNS VOID AS $$
BEGIN
    INSERT INTO CATATAN_MEDIS (
        id_hewan, username_dh, tanggal_pemeriksaan, diagnosis,
        pengobatan, status_kesehatan, catatan_tindak_lanjut
    ) VALUES (
        p_id_hewan, p_username_dh, p_tanggal_pemeriksaan, p_diagnosis,
        p_pengobatan, p_status_kesehatan, p_catatan_tindak_lanjut
    );
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 2. TRIGGER Sinkronisasi Jadwal Pemeriksaan jika Status = 'Sakit'
-- ========================================

CREATE OR REPLACE FUNCTION sinkronisasi_jadwal_pemeriksaan()
RETURNS TRIGGER AS $$
DECLARE
    tgl_baru DATE := NEW.tanggal_pemeriksaan;
    jadwal_terdekat DATE;
BEGIN
    IF NEW.status_kesehatan = 'Sakit' THEN
        -- Cari jadwal terdekat yang setelah tanggal rekam medis
        SELECT tgl_pemeriksaan_selanjutnya
        INTO jadwal_terdekat
        FROM JADWAL_PEMERIKSAAN_KESEHATAN
        WHERE id_hewan = NEW.id_hewan AND tgl_pemeriksaan_selanjutnya > tgl_baru
        ORDER BY tgl_pemeriksaan_selanjutnya ASC
        LIMIT 1;

        IF jadwal_terdekat IS NOT NULL THEN
            -- Update jadwal terdekat ke 7 hari setelah rekam medis
            UPDATE JADWAL_PEMERIKSAAN_KESEHATAN
            SET tgl_pemeriksaan_selanjutnya = tgl_baru + INTERVAL '7 days'
            WHERE id_hewan = NEW.id_hewan AND tgl_pemeriksaan_selanjutnya = jadwal_terdekat;
        ELSE
            -- Buat jadwal baru jika tidak ditemukan
            INSERT INTO JADWAL_PEMERIKSAAN_KESEHATAN(id_hewan, tgl_pemeriksaan_selanjutnya)
            VALUES (NEW.id_hewan, tgl_baru + INTERVAL '7 days');
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sinkronisasi_jadwal ON CATATAN_MEDIS;
CREATE TRIGGER trg_sinkronisasi_jadwal
AFTER INSERT ON CATATAN_MEDIS
FOR EACH ROW
EXECUTE FUNCTION sinkronisasi_jadwal_pemeriksaan();

-- ========================================
-- 3. FUNCTION Tambah Jadwal Pemeriksaan Sesuai Frekuensi Rutin
-- ========================================

CREATE OR REPLACE FUNCTION tambah_jadwal_rutin(
    p_id_hewan UUID,
    p_tanggal_awal DATE,
    p_frekuensi INT
) RETURNS VOID AS $$
DECLARE
    i INT := 1;
    next_date DATE := p_tanggal_awal;
    interval_days INTERVAL := (365 / p_frekuensi) * INTERVAL '1 day';
BEGIN
    WHILE i <= p_frekuensi LOOP
        next_date := p_tanggal_awal + (i - 1) * interval_days;
        INSERT INTO JADWAL_PEMERIKSAAN_KESEHATAN(id_hewan, tgl_pemeriksaan_selanjutnya)
        VALUES (p_id_hewan, next_date);
        i := i + 1;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 4. Tambahkan Table RIWAYAT_PAKAN untuk log pemberian pakan
-- ========================================

CREATE TABLE IF NOT EXISTS RIWAYAT_PAKAN (
    id SERIAL PRIMARY KEY,
    id_hewan UUID,
    jadwal TIMESTAMP,
    jenis_pakan VARCHAR(50),
    jumlah INT,
    status_lama VARCHAR(50),
    status_baru VARCHAR(50),
    waktu_aksi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 5. TRIGGER untuk Log Riwayat Pakan saat UPDATE status
-- ========================================

CREATE OR REPLACE FUNCTION log_riwayat_pakan_status()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO RIWAYAT_PAKAN(
        id_hewan,
        jadwal,
        jenis_pakan,
        jumlah,
        status_lama,
        status_baru
    ) VALUES (
        OLD.id_hewan,
        OLD.jadwal,
        OLD.jenis,
        OLD.jumlah,
        OLD.status,
        NEW.status
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_log_status_pakan ON PAKAN;
CREATE TRIGGER trg_log_status_pakan
AFTER UPDATE OF status ON PAKAN
FOR EACH ROW
EXECUTE FUNCTION log_riwayat_pakan_status();
