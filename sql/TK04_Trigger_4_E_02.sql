CREATE OR REPLACE FUNCTION fn_check_capacity()
RETURNS TRIGGER AS $$
DECLARE
    total_terpesan INTEGER;
    kapasitas_max INTEGER;
    sisa_tiket INTEGER;
BEGIN
    -- 🚫 Lewati jika status akan menjadi Dibatalkan
    IF NEW.status = 'Dibatalkan' THEN
        RETURN NEW;
    END IF;

    -- 🚫 Lewati jika tidak ada perubahan pada jumlah_tiket, tanggal, atau fasilitas
    IF TG_OP = 'UPDATE' AND 
       NEW.jumlah_tiket = OLD.jumlah_tiket AND 
       NEW.nama_fasilitas = OLD.nama_fasilitas AND 
       NEW.tanggal_kunjungan = OLD.tanggal_kunjungan THEN
        RETURN NEW;
    END IF;

    -- Hitung jumlah tiket yang sudah dipesan
    SELECT COALESCE(SUM(jumlah_tiket), 0)
    INTO total_terpesan
    FROM RESERVASI
    WHERE nama_fasilitas = NEW.nama_fasilitas
      AND tanggal_kunjungan = NEW.tanggal_kunjungan
      AND status != 'Cancelled'; -- Pastikan tidak menghitung yang dibatalkan

    -- Ambil kapasitas maksimum
    SELECT f.kapasitas_max
    INTO kapasitas_max
    FROM FASILITAS f
    WHERE f.nama = NEW.nama_fasilitas;

    sisa_tiket := kapasitas_max - total_terpesan;

    IF NEW.jumlah_tiket > sisa_tiket THEN
        RAISE EXCEPTION 
        'ERROR: Kapasitas tersisa "%" tiket, atraksi tidak mencukupi untuk sejumlah "%" tiket yang diminta.',
        sisa_tiket, NEW.jumlah_tiket;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trg_check_capacity ON RESERVASI;
CREATE TRIGGER trg_check_capacity
BEFORE INSERT OR UPDATE ON RESERVASI
FOR EACH ROW
EXECUTE FUNCTION fn_check_capacity();


CREATE OR REPLACE FUNCTION fn_rotasi_pelatih()
RETURNS TRIGGER AS $$
DECLARE
    tgl_awal DATE;
    durasi INTEGER;
    nama_pelatih VARCHAR;
BEGIN
    -- Ambil tanggal penugasan pertama pelatih di atraksi yang sama
    SELECT MIN(tgl_penugasan::DATE)
    INTO tgl_awal
    FROM jadwal_penugasan
    WHERE username_lh = NEW.username_lh
      AND nama_atraksi = NEW.nama_atraksi;

    -- Jika ditemukan penugasan lama
    IF tgl_awal IS NOT NULL THEN
        durasi := CURRENT_DATE - tgl_awal;

        IF durasi >= 90 THEN
            -- Ambil nama pelatih dari PENGGUNA
            SELECT nama_depan
            INTO nama_pelatih
            FROM pengguna
            WHERE username = NEW.username_lh;

            -- Tampilkan notifikasi
            RAISE NOTICE 'SUKSES: Pelatih "%" telah bertugas lebih dari 3 bulan di atraksi "%" dan akan diganti.',
                nama_pelatih, NEW.nama_atraksi;

            -- Hapus penugasan sebelumnya
            DELETE FROM jadwal_penugasan
            WHERE username_lh = NEW.username_lh
              AND nama_atraksi = NEW.nama_atraksi;

            -- Gagalkan insert baru
            RETURN NULL;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trg_rotasi_pelatih ON jadwal_penugasan;

CREATE TRIGGER trg_rotasi_pelatih
BEFORE INSERT ON jadwal_penugasan
FOR EACH ROW
EXECUTE FUNCTION fn_rotasi_pelatih();

-- Contoh penggunaan trigger rotasi pelatih
INSERT INTO jadwal_penugasan (username_lh, tgl_penugasan, nama_atraksi)
VALUES ('user76', NOW(), 'Eksibisi Reptil Langka');
