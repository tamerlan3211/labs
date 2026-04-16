-- ==========================
-- UPSERT USER
-- ==========================
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

-- ==========================
-- BULK INSERT USERS
-- ==========================
CREATE OR REPLACE PROCEDURE bulk_insert_users()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Пример: вставка тестовых данных
    INSERT INTO lalab (name, surname, phone)
    VALUES 
        ('Admin', 'System', '000'),
        ('Support', 'Tech', '111');
END;
$$;
-- ==========================
-- DELETE USER
-- ==========================
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