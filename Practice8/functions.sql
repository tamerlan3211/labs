CREATE OR REPLACE FUNCTION search_pattern(pattern TEXT)
RETURNS TABLE (
    user_id INT,
    name TEXT,
    surname TEXT,
    phone TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT user_id, name, surname, phone
    FROM lalab
    WHERE name ILIKE '%' || pattern || '%'
       OR surname ILIKE '%' || pattern || '%'
       OR phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;