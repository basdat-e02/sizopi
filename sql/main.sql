CREATE OR REPLACE FUNCTION get_user_role(p_username VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    role_name VARCHAR := 'unknown';
BEGIN
    -- Cek apakah user ada di tabel pengunjung
    IF EXISTS (SELECT 1 FROM PENGUNJUNG WHERE username_P = p_username) THEN
        IF EXISTS (SELECT 1 FROM ADOPTER WHERE username_adopter = p_username) THEN
            role_name := 'pengunjung_adopter';
        ELSE
            role_name := 'pengunjung';
        END IF;

    ELSIF EXISTS (SELECT 1 FROM DOKTER_HEWAN WHERE username_DH = p_username) THEN
        role_name := 'dokter hewan';

    ELSIF EXISTS (SELECT 1 FROM PENJAGA_HEWAN WHERE username_jh = p_username) THEN
        role_name := 'penjaga hewan';

    ELSIF EXISTS (SELECT 1 FROM STAF_ADMIN WHERE username_sa = p_username) THEN
        role_name := 'staf admin';

    ELSIF EXISTS (SELECT 1 FROM PELATIH_HEWAN WHERE username_lh = p_username) THEN
        role_name := 'pelatih pertunjukan';
    END IF;

    RETURN role_name;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION login_user(
    p_username VARCHAR,
    p_password VARCHAR
)
RETURNS TABLE (
    username_out   VARCHAR,
    email_out      VARCHAR,
    nama_depan     VARCHAR,
    nama_belakang  VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT  u.username,
            u.email,
            u.nama_depan,
            u.nama_belakang
    FROM    PENGGUNA u
    WHERE   u.username = p_username
      AND   u.password = p_password;

    /* Jika tidak ada baris yang dikembalikan */
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Username atau password salah, silakan coba lagi.';
    END IF;
END;
$$ LANGUAGE plpgsql;




/* Trigger function */
CREATE OR REPLACE FUNCTION trg_check_duplicate_username()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM PENGGUNA WHERE username = NEW.username
    ) THEN
        RAISE EXCEPTION 'ERROR: Username “%” sudah digunakan, silakan pilih username lain.', NEW.username;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

/* Trigger */
DROP TRIGGER IF EXISTS check_duplicate_username ON PENGGUNA;
CREATE TRIGGER check_duplicate_username
BEFORE INSERT ON PENGGUNA
FOR EACH ROW EXECUTE FUNCTION trg_check_duplicate_username();

