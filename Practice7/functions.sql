drop function search_pattern(pattern TEXT);
CREATE OR REPLACE FUNCTION search_pattern(pattern TEXT)

RETURNS TABLE (
    user_id INT,
    name varchar,
    surname varchar,
    phone varchar
)
AS $$
BEGIN
    RETURN QUERY
    SELECT l.user_id as user_id, l.name as name, l.surname as surname, l.phone as phone
    FROM lalab l
    WHERE l.name ILIKE '%' || pattern || '%'
       OR l.surname ILIKE '%' || pattern || '%'
       OR l.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_data_page(p_limit INT, p_offset INT)
RETURNS TABLE(
    user_id INT,
    name TEXT,
    surname TEXT,
    phone TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT user_id, name, surname, phone
    FROM lalab
    ORDER BY name
    LIMIT p_limit OFFSET p_offset;
END;
$$;
