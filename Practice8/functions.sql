CREATE OR REPLACE FUNCTION search_pattern(p_pattern TEXT)
RETURNS TABLE (
    user_id INT,
    name VARCHAR,
    surname VARCHAR,
    phone VARCHAR
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT l.user_id as user_id, l.name as name , l.surname as surname, l.phone as phone
    FROM lalab l
    WHERE l.name ILIKE "%" || p_pattern || "%"
       OR l.surname ILIKE "%" || p_pattern || "%" 
       OR l.phone ILIKE "%" || p_pattern || "%";
END;
$$;
-- ==========================
-- PAGINATION / GET DATA PAGE
CREATE OR REPLACE FUNCTION get_data_page(p_limit INT, p_offset INT)
RETURNS TABLE (
    user_id INT,
    name VARCHAR,
    surname VARCHAR,
    phone VARCHAR
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT l.user_id, l.name, l.surname, l.phone -- Добавили "l." перед каждым полем
    FROM lalab l                                -- Дали таблице алиас "l"
    ORDER BY l.name
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;