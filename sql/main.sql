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


CREATE OR REPLACE FUNCTION register_pengguna (
    p_username      VARCHAR,
    p_email         VARCHAR,
    p_password      VARCHAR,
    p_nama_depan    VARCHAR,
    p_nama_tengah   VARCHAR,
    p_nama_belakang VARCHAR,
    p_no_telepon    VARCHAR
) RETURNS VOID AS $$
BEGIN
    INSERT INTO PENGGUNA(username, email, password,
                          nama_depan, nama_tengah, nama_belakang, no_telepon)
    VALUES (p_username, p_email, p_password,
            p_nama_depan, p_nama_tengah, p_nama_belakang, p_no_telepon);
    /* → kalau username duplikat, trigger me-RAISE EXCEPTION di sini */
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION register_pengunjung (
    p_username      VARCHAR,
    p_email         VARCHAR,
    p_password      VARCHAR,
    p_nama_depan    VARCHAR,
    p_nama_tengah   VARCHAR,
    p_nama_belakang VARCHAR,
    p_no_telepon    VARCHAR,
    p_alamat        VARCHAR,
    p_tgl_lahir     DATE
) RETURNS VOID AS $$
BEGIN
    PERFORM register_pengguna(p_username, p_email, p_password,
                              p_nama_depan, p_nama_tengah, p_nama_belakang,
                              p_no_telepon);

    INSERT INTO PENGUNJUNG(username_P, alamat, tgl_lahir)
    VALUES (p_username, p_alamat, p_tgl_lahir);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION register_dokter_hewan (
    p_username      VARCHAR,
    p_email         VARCHAR,
    p_password      VARCHAR,
    p_nama_depan    VARCHAR,
    p_nama_tengah   VARCHAR,
    p_nama_belakang VARCHAR,
    p_no_telepon    VARCHAR,
    p_no_str        VARCHAR,
    p_spesialisasi  TEXT[]          -- array 1..N
) RETURNS VOID AS $$
DECLARE
    sp TEXT;
BEGIN
    PERFORM register_pengguna(p_username, p_email, p_password,
                              p_nama_depan, p_nama_tengah, p_nama_belakang,
                              p_no_telepon);

    INSERT INTO DOKTER_HEWAN(username_DH, no_STR)
    VALUES (p_username, p_no_str);

    FOREACH sp IN ARRAY p_spesialisasi LOOP
        INSERT INTO SPESIALISASI(username_SH, nama_spesialisasi)
        VALUES (p_username, sp);
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION register_staff (
    p_username      VARCHAR,
    p_email         VARCHAR,
    p_password      VARCHAR,
    p_nama_depan    VARCHAR,
    p_nama_tengah   VARCHAR,
    p_nama_belakang VARCHAR,
    p_no_telepon    VARCHAR,
    p_role_code     VARCHAR        -- 'PJH' | 'ADM' | 'PLP'
) RETURNS VOID AS $$
DECLARE
    v_table TEXT;
    v_col   TEXT;
    v_id    UUID := gen_random_uuid();
BEGIN
    PERFORM register_pengguna(p_username, p_email, p_password,
                              p_nama_depan, p_nama_tengah, p_nama_belakang,
                              p_no_telepon);

    CASE p_role_code
        WHEN 'PJH' THEN v_table := 'penjaga_hewan';   v_col := 'username_jh';
        WHEN 'ADM' THEN v_table := 'staf_admin';      v_col := 'username_sa';
        WHEN 'PLP' THEN v_table := 'pelatih_hewan';   v_col := 'username_lh';
        ELSE
            RAISE EXCEPTION 'Peran staff tidak valid. Gunakan PJH/ADM/PLP.';
    END CASE;

    EXECUTE format(
        'INSERT INTO %I(%I, id_staf) VALUES ($1, $2)',
        v_table, v_col
    ) USING p_username, v_id;
END;
$$ LANGUAGE plpgsql;


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


DROP TRIGGER IF EXISTS check_duplicate_username ON PENGGUNA;
CREATE TRIGGER check_duplicate_username
BEFORE INSERT ON PENGGUNA
FOR EACH ROW EXECUTE FUNCTION trg_check_duplicate_username();

