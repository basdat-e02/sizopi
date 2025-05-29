-- HABITAT Table CRUD Operations

-- CREATE (Insert) Operation for HABITAT
CREATE OR REPLACE FUNCTION insert_habitat(
    p_nama VARCHAR(50),
    p_luas_area DECIMAL,
    p_kapasitas INT,
    p_status VARCHAR(100)
) RETURNS VOID AS $$
BEGIN
    INSERT INTO HABITAT (nama, luas_area, kapasitas, status)
    VALUES (p_nama, p_luas_area, p_kapasitas, p_status);
END;
$$ LANGUAGE plpgsql;

-- READ Operations for HABITAT
CREATE OR REPLACE FUNCTION get_all_habitats() 
RETURNS TABLE (
    nama VARCHAR(50),
    luas_area DECIMAL,
    kapasitas INT,
    status VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY SELECT h.nama, h.luas_area, h.kapasitas, h.status FROM HABITAT h;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_habitat_by_name(p_nama VARCHAR(50))
RETURNS TABLE (
    nama VARCHAR(50),
    luas_area DECIMAL,
    kapasitas INT,
    status VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY SELECT h.nama, h.luas_area, h.kapasitas, h.status 
    FROM HABITAT h
    WHERE h.nama = p_nama;
END;
$$ LANGUAGE plpgsql;

-- UPDATE Operation for HABITAT
CREATE OR REPLACE FUNCTION update_habitat(
    p_nama VARCHAR(50),
    p_luas_area DECIMAL,
    p_kapasitas INT,
    p_status VARCHAR(100)
) RETURNS VOID AS $$
BEGIN
    UPDATE HABITAT
    SET luas_area = p_luas_area,
        kapasitas = p_kapasitas,
        status = p_status
    WHERE nama = p_nama;
END;
$$ LANGUAGE plpgsql;

-- DELETE Operation for HABITAT
CREATE OR REPLACE FUNCTION delete_habitat(p_nama VARCHAR(50))
RETURNS VOID AS $$
BEGIN
    DELETE FROM HABITAT WHERE nama = p_nama;
END;
$$ LANGUAGE plpgsql;

-- HEWAN Table CRUD Operations

-- CREATE (Insert) Operation for HEWAN
CREATE OR REPLACE FUNCTION insert_hewan(
    p_nama VARCHAR(100),
    p_spesies VARCHAR(100),
    p_asal_hewan VARCHAR(100),
    p_tanggal_lahir DATE,
    p_status_kesehatan VARCHAR(50),
    p_nama_habitat VARCHAR(50),
    p_url_foto VARCHAR(255)
) RETURNS UUID AS $$
DECLARE
    new_id UUID := gen_random_uuid();
BEGIN
    INSERT INTO HEWAN (id, nama, spesies, asal_hewan, tanggal_lahir, status_kesehatan, nama_habitat, url_foto)
    VALUES (new_id, p_nama, p_spesies, p_asal_hewan, p_tanggal_lahir, p_status_kesehatan, p_nama_habitat, p_url_foto);
    
    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

-- READ Operations for HEWAN
CREATE OR REPLACE FUNCTION get_all_hewan()
RETURNS TABLE (
    id UUID,
    nama VARCHAR(100),
    spesies VARCHAR(100),
    asal_hewan VARCHAR(100),
    tanggal_lahir DATE,
    status_kesehatan VARCHAR(50),
    nama_habitat VARCHAR(50),
    url_foto VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY SELECT h.id, h.nama, h.spesies, h.asal_hewan, h.tanggal_lahir, h.status_kesehatan, h.nama_habitat, h.url_foto
    FROM HEWAN h;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_hewan_by_id(p_id UUID)
RETURNS TABLE (
    id UUID,
    nama VARCHAR(100),
    spesies VARCHAR(100),
    asal_hewan VARCHAR(100),
    tanggal_lahir DATE,
    status_kesehatan VARCHAR(50),
    nama_habitat VARCHAR(50),
    url_foto VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY SELECT h.id, h.nama, h.spesies, h.asal_hewan, h.tanggal_lahir, h.status_kesehatan, h.nama_habitat, h.url_foto
    FROM HEWAN h
    WHERE h.id = p_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_hewan_by_habitat(p_nama_habitat VARCHAR(50))
RETURNS TABLE (
    id UUID,
    nama VARCHAR(100),
    spesies VARCHAR(100),
    asal_hewan VARCHAR(100),
    tanggal_lahir DATE,
    status_kesehatan VARCHAR(50),
    nama_habitat VARCHAR(50),
    url_foto VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY SELECT h.id, h.nama, h.spesies, h.asal_hewan, h.tanggal_lahir, h.status_kesehatan, h.nama_habitat, h.url_foto
    FROM HEWAN h
    WHERE h.nama_habitat = p_nama_habitat;
END;
$$ LANGUAGE plpgsql;

-- UPDATE Operation for HEWAN
CREATE OR REPLACE FUNCTION update_hewan(
    p_id UUID,
    p_nama VARCHAR(100),
    p_spesies VARCHAR(100),
    p_asal_hewan VARCHAR(100),
    p_tanggal_lahir DATE,
    p_status_kesehatan VARCHAR(50),
    p_nama_habitat VARCHAR(50),
    p_url_foto VARCHAR(255)
) RETURNS VOID AS $$
BEGIN
    UPDATE HEWAN
    SET nama = p_nama,
        spesies = p_spesies,
        asal_hewan = p_asal_hewan,
        tanggal_lahir = p_tanggal_lahir,
        status_kesehatan = p_status_kesehatan,
        nama_habitat = p_nama_habitat,
        url_foto = p_url_foto
    WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;

-- UPDATE specific field: Status Kesehatan
CREATE OR REPLACE FUNCTION update_hewan_kesehatan(
    p_id UUID,
    p_status_kesehatan VARCHAR(50)
) RETURNS VOID AS $$
BEGIN
    UPDATE HEWAN
    SET status_kesehatan = p_status_kesehatan
    WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;

-- UPDATE specific field: Habitat
CREATE OR REPLACE FUNCTION update_hewan_habitat(
    p_id UUID,
    p_nama_habitat VARCHAR(50)
) RETURNS VOID AS $$
BEGIN
    UPDATE HEWAN
    SET nama_habitat = p_nama_habitat
    WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;

-- DELETE Operation for HEWAN
CREATE OR REPLACE FUNCTION delete_hewan(p_id UUID)
RETURNS VOID AS $$
BEGIN
    DELETE FROM HEWAN WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;


/* Trigger function */
CREATE OR REPLACE FUNCTION trg_check_duplicate_hewan()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM HEWAN
        WHERE lower(nama)        = lower(NEW.nama)
          AND lower(spesies)     = lower(NEW.spesies)
          AND lower(asal_hewan)  = lower(NEW.asal_hewan)
    ) THEN
        RAISE EXCEPTION
            'Data satwa atas nama “%”, spesies “%”, dan berasal dari “%” sudah terdaftar.',
            NEW.nama, NEW.spesies, NEW.asal_hewan;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

/* Trigger */
DROP TRIGGER IF EXISTS check_duplicate_hewan ON HEWAN;
CREATE TRIGGER check_duplicate_hewan
BEFORE INSERT ON HEWAN
FOR EACH ROW EXECUTE FUNCTION trg_check_duplicate_hewan();


CREATE OR REPLACE FUNCTION trg_log_hewan_update()
RETURNS TRIGGER AS $$
DECLARE
    msg TEXT;
BEGIN
    /* ----- status_kesehatan ----- */
    INSERT INTO RIWAYAT_SATWA (id_hewan, kolom_diubah, sebelum, sesudah)
    VALUES (NEW.id, 'status_kesehatan', OLD.status_kesehatan, NEW.status_kesehatan);

    /* ----- nama_habitat ----- */
    INSERT INTO RIWAYAT_SATWA (id_hewan, kolom_diubah, sebelum, sesudah)
    VALUES (NEW.id, 'nama_habitat', OLD.nama_habitat, NEW.nama_habitat);

    /* Pesan sukses – selalu muncul, walau sebelum=sesudah */
    msg := format(
        'SUKSES: Riwayat perubahan status kesehatan dari “%s” menjadi “%s” atau habitat dari “%s” menjadi “%s” telah dicatat.',
        COALESCE(OLD.status_kesehatan,'-'), COALESCE(NEW.status_kesehatan,'-'),
        COALESCE(OLD.nama_habitat,'-'),     COALESCE(NEW.nama_habitat,'-')
    );
    RAISE NOTICE '%', msg;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS log_hewan_update ON HEWAN;
CREATE TRIGGER log_hewan_update
AFTER UPDATE OF status_kesehatan, nama_habitat ON HEWAN
FOR EACH ROW EXECUTE FUNCTION trg_log_hewan_update();

CREATE OR REPLACE FUNCTION trg_habitat_no_shrink_below_current ()
RETURNS trigger AS
$$
DECLARE
    current_count INT;
BEGIN
    /* Jalankan hanya jika kapasitas BERKURANG */
    IF NEW.kapasitas < OLD.kapasitas THEN
        SELECT COUNT(*)
          INTO current_count
          FROM hewan
         WHERE nama_habitat = NEW.nama;

        IF NEW.kapasitas < current_count THEN
            RAISE EXCEPTION
              'Tidak dapat menurunkan kapasitas habitat % ke % karena sudah ada % hewan.',
              NEW.nama, NEW.kapasitas, current_count;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS habitat_check_shrink ON habitat;
CREATE TRIGGER habitat_check_shrink
BEFORE UPDATE OF kapasitas
ON habitat
FOR EACH ROW
EXECUTE FUNCTION trg_habitat_no_shrink_below_current();



CREATE OR REPLACE FUNCTION trg_hewan_check_capacity ()
RETURNS trigger AS
$$
DECLARE
    max_capacity   INT;
    current_count  INT;
BEGIN
    /* 1. Jika NEW.nama_habitat NULL, aturan tak berlaku */
    IF NEW.nama_habitat IS NULL THEN
        RETURN NEW;
    END IF;

    /* 2. Kunci baris habitat untuk konsistensi */
    SELECT kapasitas
      INTO max_capacity
      FROM habitat
     WHERE nama = NEW.nama_habitat
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Habitat % tidak ditemukan.', NEW.nama_habitat;
    END IF;

    /* 3. Hitung hewan di habitat (abaikan diri sendiri saat UPDATE) */
    SELECT COUNT(*)
      INTO current_count
      FROM hewan
     WHERE nama_habitat = NEW.nama_habitat
       AND (TG_OP = 'INSERT' OR id <> OLD.id);

    IF current_count >= max_capacity THEN
        RAISE EXCEPTION
          'Habitat % penuh: kapasitas %, hewan_saat_ini %.',
          NEW.nama_habitat,          -- 1st %
          max_capacity,              -- 2nd %
          current_count;             -- 3rd %
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS hewan_check_capacity ON hewan;
CREATE TRIGGER hewan_check_capacity
BEFORE INSERT OR UPDATE OF nama_habitat
ON hewan
FOR EACH ROW
EXECUTE FUNCTION trg_hewan_check_capacity();
