-- ==============================================
-- A. ADOPTER, INDIVIDU, ORGANISASI (tanpa perubahan)
-- ==============================================

-- 1. INSERT Adopter Individu
CREATE OR REPLACE FUNCTION insert_adopter_individu(
  p_username VARCHAR,
  p_nik       VARCHAR,
  p_nama      VARCHAR
) RETURNS UUID AS $$
DECLARE
  new_id UUID := gen_random_uuid();
BEGIN
  INSERT INTO ADOPTER (id_adopter, username_adopter, total_kontribusi)
    VALUES (new_id, p_username, 0);
  INSERT INTO INDIVIDU (id_adopter, nik, nama)
    VALUES (new_id, p_nik, p_nama);
  RETURN new_id;
END;
$$ LANGUAGE plpgsql;

-- 2. INSERT Adopter Organisasi
CREATE OR REPLACE FUNCTION insert_adopter_organisasi(
  p_username VARCHAR,
  p_npp       VARCHAR,
  p_nama_org  VARCHAR
) RETURNS UUID AS $$
DECLARE
  new_id UUID := gen_random_uuid();
BEGIN
  INSERT INTO ADOPTER (id_adopter, username_adopter, total_kontribusi)
    VALUES (new_id, p_username, 0);
  INSERT INTO ORGANISASI (id_adopter, npp, nama_organisasi)
    VALUES (new_id, p_npp, p_nama_org);
  RETURN new_id;
END;
$$ LANGUAGE plpgsql;

-- 3. READ semua Adopter
CREATE OR REPLACE FUNCTION get_all_adopters()
RETURNS TABLE (
  id_adopter       UUID,
  username_adopter VARCHAR,
  tipe             VARCHAR,
  nama             VARCHAR,
  identifier       VARCHAR,
  total_kontribusi INT
) AS $$
BEGIN
  RETURN QUERY
    SELECT 
      a.id_adopter,
      a.username_adopter,
      CASE WHEN i.nik IS NOT NULL THEN 'Individu' ELSE 'Organisasi' END,
      COALESCE(i.nama, o.nama_organisasi),
      COALESCE(i.nik, o.npp),
      a.total_kontribusi
    FROM ADOPTER a
    LEFT JOIN INDIVIDU    i ON i.id_adopter = a.id_adopter
    LEFT JOIN ORGANISASI o ON o.id_adopter = a.id_adopter;
END;
$$ LANGUAGE plpgsql;

-- 4. READ Adopter by ID
CREATE OR REPLACE FUNCTION get_adopter_by_id(p_id UUID)
RETURNS TABLE (
  id_adopter       UUID,
  username_adopter VARCHAR,
  tipe             VARCHAR,
  nama             VARCHAR,
  identifier       VARCHAR,
  total_kontribusi INT
) AS $$
BEGIN
  RETURN QUERY
    SELECT * 
      FROM get_all_adopters()
     WHERE id_adopter = p_id;
END;
$$ LANGUAGE plpgsql;

-- 5. UPDATE Adopter Username
CREATE OR REPLACE FUNCTION update_adopter_username(
  p_id       UUID,
  p_username VARCHAR
) RETURNS VOID AS $$
BEGIN
  UPDATE ADOPTER
     SET username_adopter = p_username
   WHERE id_adopter = p_id;
END;
$$ LANGUAGE plpgsql;

-- 6. DELETE Adopter
CREATE OR REPLACE FUNCTION delete_adopter(p_id UUID)
RETURNS VOID AS $$
BEGIN
  DELETE FROM ADOPTER
   WHERE id_adopter = p_id;
END;
$$ LANGUAGE plpgsql;


-- ==============================================
-- B. ADOPSI (composite PK; TANPA kolom id_adopsi)
-- ==============================================

-- 1. INSERT Adopsi
CREATE OR REPLACE FUNCTION insert_adopsi(
  p_id_adopter           UUID,
  p_id_hewan             UUID,
  p_tgl_mulai_adopsi     DATE,
  p_tgl_berhenti_adopsi  DATE,
  p_kontribusi_finansial INT,
  p_status               VARCHAR
) RETURNS VOID AS $$
BEGIN
  INSERT INTO ADOPSI (
    id_adopter, id_hewan,
    tgl_mulai_adopsi, tgl_berhenti_adopsi,
    kontribusi_finansial, status_pembayaran
  )
  VALUES (
    p_id_adopter, p_id_hewan,
    p_tgl_mulai_adopsi, p_tgl_berhenti_adopsi,
    p_kontribusi_finansial, p_status
  );
END;
$$ LANGUAGE plpgsql;

-- 2. READ semua Adopsi
CREATE OR REPLACE FUNCTION get_all_adopsi()
RETURNS TABLE (
  id_adopter           UUID,
  id_hewan             UUID,
  tgl_mulai_adopsi     DATE,
  tgl_berhenti_adopsi  DATE,
  kontribusi_finansial INT,
  status_pembayaran    VARCHAR
) AS $$
BEGIN
  RETURN QUERY
    SELECT
      ad.id_adopter,
      ad.id_hewan,
      ad.tgl_mulai_adopsi,
      ad.tgl_berhenti_adopsi,
      ad.kontribusi_finansial,
      ad.status_pembayaran
    FROM ADOPSI ad;
END;
$$ LANGUAGE plpgsql;

-- 3. READ Adopsi by composite PK
CREATE OR REPLACE FUNCTION get_adopsi_by_pk(
  p_id_adopter       UUID,
  p_id_hewan         UUID,
  p_tgl_mulai_adopsi DATE
) RETURNS TABLE (
  id_adopter           UUID,
  id_hewan             UUID,
  tgl_mulai_adopsi     DATE,
  tgl_berhenti_adopsi  DATE,
  kontribusi_finansial INT,
  status_pembayaran    VARCHAR
) AS $$
BEGIN
  RETURN QUERY
    SELECT
      ad.id_adopter,
      ad.id_hewan,
      ad.tgl_mulai_adopsi,
      ad.tgl_berhenti_adopsi,
      ad.kontribusi_finansial,
      ad.status_pembayaran
    FROM ADOPSI ad
   WHERE ad.id_adopter       = p_id_adopter
     AND ad.id_hewan         = p_id_hewan
     AND ad.tgl_mulai_adopsi = p_tgl_mulai_adopsi;
END;
$$ LANGUAGE plpgsql;

-- 4. UPDATE Adopsi by composite PK
CREATE OR REPLACE FUNCTION update_adopsi(
  p_id_adopter           UUID,
  p_id_hewan             UUID,
  p_tgl_mulai_adopsi     DATE,
  p_tgl_berhenti_adopsi  DATE,
  p_kontribusi_finansial INT,
  p_status               VARCHAR
) RETURNS VOID AS $$
BEGIN
  UPDATE ADOPSI
     SET tgl_berhenti_adopsi  = p_tgl_berhenti_adopsi,
         kontribusi_finansial = p_kontribusi_finansial,
         status_pembayaran    = p_status
   WHERE id_adopter       = p_id_adopter
     AND id_hewan         = p_id_hewan
     AND tgl_mulai_adopsi = p_tgl_mulai_adopsi;
END;
$$ LANGUAGE plpgsql;

-- 5. DELETE Adopsi by composite PK
CREATE OR REPLACE FUNCTION delete_adopsi(
  p_id_adopter       UUID,
  p_id_hewan         UUID,
  p_tgl_mulai_adopsi DATE
) RETURNS VOID AS $$
BEGIN
  DELETE FROM ADOPSI
   WHERE id_adopter       = p_id_adopter
     AND id_hewan         = p_id_hewan
     AND tgl_mulai_adopsi = p_tgl_mulai_adopsi;
END;
$$ LANGUAGE plpgsql;


-- ==============================================
-- C. TRIGGER: Sinkronisasi Total Kontribusi
-- ==============================================
CREATE OR REPLACE FUNCTION trg_sync_total_kontribusi()
RETURNS TRIGGER AS $$
DECLARE
  total INT;
BEGIN
  SELECT COALESCE(SUM(kontribusi_finansial),0)
    INTO total
    FROM ADOPSI
   WHERE id_adopter = NEW.id_adopter
     AND status_pembayaran = 'lunas';

  UPDATE ADOPTER
     SET total_kontribusi = total
   WHERE id_adopter = NEW.id_adopter;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS sync_total_kontribusi ON ADOPSI;
CREATE TRIGGER sync_total_kontribusi
  AFTER INSERT OR UPDATE OF status_pembayaran,kontribusi_finansial
  ON ADOPSI
  FOR EACH ROW EXECUTE FUNCTION trg_sync_total_kontribusi();
