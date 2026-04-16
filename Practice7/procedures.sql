
CREATE OR REPLACE PROCEDURE upsert_user(
    p_name TEXT,
    p_surname TEXT,
    p_phone TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS(SELECT 1 FROM lalab WHERE name = p_name AND surname = p_surname) THEN
        UPDATE lalab
        SET phone = p_phone
        WHERE name = p_name AND surname = p_surname;
    ELSE
        INSERT INTO lalab(name, surname, phone)
        VALUES(p_name, p_surname, p_phone);
    END IF;
END;
$$;


-- ========================================

CREATE OR REPLACE PROCEDURE bulk_insert_users()
LANGUAGE plpgsql
AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT * FROM temp_users LOOP
        PERFORM upsert_user(r.name, r.surname, r.phone);
    END LOOP;
END;
$$;


-- ========================================

CREATE OR REPLACE PROCEDURE delete_user(
    p_name TEXT DEFAULT NULL,
    p_phone TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM lalab
    WHERE (p_name IS NOT NULL AND name = p_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);
END;
$$;