-- =============================================================
-- procedures.sql  —  TSIS1 New Stored Procedures & Functions
-- These are NEW objects only — Practice 8 objects are NOT repeated.
-- =============================================================

-- -------------------------------------------------------------
-- 3.4 a)  add_phone
--   Adds a phone number to an existing contact (looked up by name).
--   Raises a notice if the contact is not found.
-- -------------------------------------------------------------
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Find the contact (case-insensitive, first match)
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(name) = LOWER(p_contact_name)
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE NOTICE 'Contact "%" not found.', p_contact_name;
        RETURN;
    END IF;

    -- Prevent exact duplicate phone for the same contact
    IF EXISTS (
        SELECT 1 FROM phones
        WHERE contact_id = v_contact_id AND phone = p_phone
    ) THEN
        RAISE NOTICE 'Phone % already exists for contact %.', p_phone, p_contact_name;
        RETURN;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact %.', p_phone, p_type, p_contact_name;
END;
$$;


-- -------------------------------------------------------------
-- 3.4 b)  move_to_group
--   Moves a contact to a group; creates the group if it does not exist.
-- -------------------------------------------------------------
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Ensure the group exists (upsert)
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- Find the contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(name) = LOWER(p_contact_name)
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE NOTICE 'Contact "%" not found.', p_contact_name;
        RETURN;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- -------------------------------------------------------------
-- 3.4 c)  search_contacts
--   Extended pattern search: name, surname, email, AND all phones
--   in the phones table.  Returns distinct contacts.
-- -------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    name       VARCHAR,
    surname    VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    grp        VARCHAR,
    phones_list TEXT        -- comma-separated list of all phones
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id                                          AS contact_id,
        c.name,
        c.surname,
        c.email,
        c.birthday,
        g.name                                        AS grp,
        STRING_AGG(p.phone || ' (' || p.type || ')', ', '
                   ORDER BY p.type)                   AS phones_list
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.name    ILIKE '%' || p_query || '%'
        OR c.surname ILIKE '%' || p_query || '%'
        OR c.email   ILIKE '%' || p_query || '%'
        OR EXISTS (
            SELECT 1 FROM phones ph
            WHERE ph.contact_id = c.id
              AND ph.phone ILIKE '%' || p_query || '%'
        )
    GROUP BY c.id, c.name, c.surname, c.email, c.birthday, g.name
    ORDER BY c.name;
END;
$$;


-- -------------------------------------------------------------
-- Helper: get_contacts_page  (pagination, extended columns)
-- -------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_contacts_page(
    p_limit  INT,
    p_offset INT,
    p_sort   TEXT DEFAULT 'name'   -- 'name' | 'birthday' | 'created_at'
)
RETURNS TABLE (
    contact_id  INTEGER,
    name        VARCHAR,
    surname     VARCHAR,
    email       VARCHAR,
    birthday    DATE,
    grp         VARCHAR,
    phones_list TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        $q$
        SELECT
            c.id,
            c.name,
            c.surname,
            c.email,
            c.birthday,
            g.name,
            STRING_AGG(p.phone || ' (' || p.type || ')', ', ' ORDER BY p.type)
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        GROUP BY c.id, c.name, c.surname, c.email, c.birthday, g.name, c.created_at
        ORDER BY %I
        LIMIT %s OFFSET %s
        $q$,
        p_sort, p_limit, p_offset
    );
END;
$$;
