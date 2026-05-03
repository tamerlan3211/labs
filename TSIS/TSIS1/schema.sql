-- =============================================================
-- schema.sql  —  TSIS1 PhoneBook Extended Schema
-- Run once to set up (or upgrade) the database.
-- =============================================================

-- 1. Groups / Categories
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed default categories
INSERT INTO groups (name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- 2. Main contacts table
--    (Rename your existing "lalab" table if needed, or adjust the name below)
CREATE TABLE IF NOT EXISTS contacts (
    id        SERIAL PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    surname   VARCHAR(100) NOT NULL,
    email     VARCHAR(100),
    birthday  DATE,
    group_id  INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Phones (1-to-many, replaces the single phone column)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile')) DEFAULT 'mobile'
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_contacts_name    ON contacts (LOWER(name));
CREATE INDEX IF NOT EXISTS idx_contacts_email   ON contacts (LOWER(email));
CREATE INDEX IF NOT EXISTS idx_phones_contact   ON phones   (contact_id);
CREATE INDEX IF NOT EXISTS idx_phones_phone     ON phones   (phone);
