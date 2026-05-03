"""
phonebook.py  —  TSIS1 Extended PhoneBook
Builds on Practice 7 & 8.  New features only (no re-implementation of base CRUD).
"""

import psycopg2
import csv
import json
import sys
from datetime import date, datetime
from config import load_config

# ─────────────────── DB helper ────────────────────────────────────────────────

def _conn():
    """Return a fresh psycopg2 connection."""
    return psycopg2.connect(**load_config())


def _exec(sql, params=(), fetch='none'):
    """Execute *sql* and optionally return rows."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            if fetch == 'one':
                return cur.fetchone()
            if fetch == 'all':
                return cur.fetchall()
            if fetch == 'col':          # column names
                return [d[0] for d in cur.description]


# ─────────────────── 3.1  Extended Contact Model ──────────────────────────────

def _ensure_group(group_name: str, conn) -> int:
    """Insert group if missing; return its id."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
            (group_name,)
        )
        cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
        return cur.fetchone()[0]


def insert_contact(name: str, surname: str,
                   email: str = None, birthday: str = None,
                   group_name: str = None) -> int:
    """Insert a contact (no phones).  Returns new contact id."""
    with _conn() as conn:
        group_id = _ensure_group(group_name, conn) if group_name else None
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO contacts (name, surname, email, birthday, group_id)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id;""",
                (name, surname, email or None,
                 birthday or None, group_id)
            )
            contact_id = cur.fetchone()[0]
        conn.commit()
    print(f"  ✓ Contact inserted  id={contact_id}")
    return contact_id


def add_phone_py(contact_id: int, phone: str, phone_type: str = 'mobile'):
    """Python-side add_phone (calls stored procedure)."""
    with _conn() as conn:
        with conn.cursor() as cur:
            # Use the PL/pgSQL procedure from procedures.sql
            cur.execute(
                "SELECT name FROM contacts WHERE id = %s;", (contact_id,)
            )
            row = cur.fetchone()
            if not row:
                print(f"  ✗ Contact id={contact_id} not found.")
                return
            cur.execute(
                "CALL add_phone(%s, %s, %s);",
                (row[0], phone, phone_type)
            )
        conn.commit()
    print(f"  ✓ Phone {phone} ({phone_type}) added to contact id={contact_id}")


# ─────────────────── 3.2  Advanced Search & Filter ────────────────────────────

def filter_by_group(group_name: str):
    """Show all contacts in a given group."""
    rows = _exec(
        """SELECT c.id, c.name, c.surname, c.email, c.birthday,
                  STRING_AGG(p.phone || ' (' || p.type || ')', ', ') AS phones
           FROM contacts c
           LEFT JOIN groups  g ON g.id = c.group_id
           LEFT JOIN phones  p ON p.contact_id = c.id
           WHERE LOWER(g.name) = LOWER(%s)
           GROUP BY c.id, c.name, c.surname, c.email, c.birthday
           ORDER BY c.name;""",
        (group_name,), fetch='all'
    )
    _print_rows(rows, ["id", "name", "surname", "email", "birthday", "phones"])


def search_by_email(pattern: str):
    """Partial email match."""
    rows = _exec(
        """SELECT c.id, c.name, c.surname, c.email,
                  STRING_AGG(p.phone || ' (' || p.type || ')', ', ') AS phones
           FROM contacts c
           LEFT JOIN phones p ON p.contact_id = c.id
           WHERE c.email ILIKE %s
           GROUP BY c.id, c.name, c.surname, c.email
           ORDER BY c.name;""",
        ('%' + pattern + '%',), fetch='all'
    )
    _print_rows(rows, ["id", "name", "surname", "email", "phones"])


def list_sorted(sort_by: str = 'name'):
    """Show all contacts sorted by name / birthday / created_at."""
    allowed = {'name', 'birthday', 'created_at'}
    if sort_by not in allowed:
        print(f"  ✗ sort_by must be one of: {allowed}")
        return
    # Dynamic ORDER BY — safe because we whitelist the value above
    sql = f"""
        SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name AS grp,
               STRING_AGG(p.phone || ' (' || p.type || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        GROUP BY c.id, c.name, c.surname, c.email, c.birthday, g.name, c.created_at
        ORDER BY c.{sort_by} NULLS LAST;
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    _print_rows(rows, ["id", "name", "surname", "email", "birthday", "group", "phones"])


def paginated_browse(page_size: int = 5, sort_by: str = 'name'):
    """Interactive page navigator using get_contacts_page()."""
    offset = 0
    while True:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM get_contacts_page(%s, %s, %s);",
                    (page_size, offset, sort_by)
                )
                rows = cur.fetchall()
        if not rows:
            print("  (no more records)")
            if offset == 0:
                return
            offset = max(0, offset - page_size)
            continue
        _print_rows(rows, ["id", "name", "surname", "email", "birthday", "group", "phones"])
        cmd = input("\n  [n]ext  [p]rev  [q]uit > ").strip().lower()
        if cmd == 'n':
            offset += page_size
        elif cmd == 'p':
            offset = max(0, offset - page_size)
        else:
            break


# ─────────────────── 3.3  Import / Export ─────────────────────────────────────

# ── JSON export ───────────────────────────────────────────────────────────────

def export_to_json(filename: str = 'contacts_export.json'):
    """Export all contacts (with phones and group) to JSON."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.surname, c.email,
                       c.birthday::TEXT, g.name AS grp,
                       JSON_AGG(
                           JSON_BUILD_OBJECT('phone', p.phone, 'type', p.type)
                           ORDER BY p.type
                       ) FILTER (WHERE p.id IS NOT NULL) AS phones
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                GROUP BY c.id, c.name, c.surname, c.email, c.birthday, g.name
                ORDER BY c.name;
            """)
            rows = cur.fetchall()

    data = []
    for r in rows:
        data.append({
            "id":       r[0],
            "name":     r[1],
            "surname":  r[2],
            "email":    r[3],
            "birthday": r[4],
            "group":    r[5],
            "phones":   r[6] or [],
        })

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Exported {len(data)} contacts → {filename}")


# ── JSON import ───────────────────────────────────────────────────────────────

def import_from_json(filename: str = 'contacts_export.json'):
    """
    Import contacts from a JSON file.
    On duplicate (same name + surname): ask user to skip or overwrite.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            entries = json.load(f)
    except FileNotFoundError:
        print(f"  ✗ File not found: {filename}")
        return
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON parse error: {e}")
        return

    inserted = skipped = overwritten = 0

    with _conn() as conn:
        for entry in entries:
            name    = entry.get('name', '').strip()
            surname = entry.get('surname', '').strip()
            if not name:
                continue

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM contacts WHERE LOWER(name)=LOWER(%s) AND LOWER(surname)=LOWER(%s);",
                    (name, surname)
                )
                existing = cur.fetchone()

            if existing:
                choice = input(
                    f"  Contact '{name} {surname}' already exists. "
                    f"[s]kip / [o]verwrite? "
                ).strip().lower()
                if choice != 'o':
                    skipped += 1
                    continue
                # Overwrite: delete old record (CASCADE removes phones)
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM contacts WHERE id = %s;", (existing[0],))
                overwritten += 1

            group_id = _ensure_group(entry['group'], conn) if entry.get('group') else None

            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO contacts (name, surname, email, birthday, group_id)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id;""",
                    (name, surname,
                     entry.get('email') or None,
                     entry.get('birthday') or None,
                     group_id)
                )
                cid = cur.fetchone()[0]
                for ph in (entry.get('phones') or []):
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                        (cid, ph['phone'], ph.get('type', 'mobile'))
                    )
            inserted += 1

        conn.commit()

    print(f"  ✓ Import done — inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}")


# ── Extended CSV import (new fields) ─────────────────────────────────────────

def import_from_csv(filename: str):
    """
    Extended CSV importer.
    Expected columns: name, surname, email, birthday, group, phone, phone_type
    Multiple rows with the same name+surname are merged (phones aggregated).
    """
    try:
        f = open(filename, 'r', encoding='utf-8')
    except FileNotFoundError:
        print(f"  ✗ File not found: {filename}")
        return

    # Aggregate multi-phone rows by (name, surname)
    contacts: dict = {}
    with f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            key = (row.get('name', '').strip(), row.get('surname', '').strip())
            if not key[0]:
                print(f"  Row {i} skipped — missing name")
                continue
            if key not in contacts:
                contacts[key] = {
                    'email':    row.get('email', '').strip() or None,
                    'birthday': row.get('birthday', '').strip() or None,
                    'group':    row.get('group', '').strip() or None,
                    'phones':   [],
                }
            ph = row.get('phone', '').strip()
            pt = row.get('phone_type', 'mobile').strip() or 'mobile'
            if ph:
                contacts[key]['phones'].append((ph, pt))

    inserted = skipped = 0
    with _conn() as conn:
        for (name, surname), data in contacts.items():
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM contacts WHERE LOWER(name)=LOWER(%s) AND LOWER(surname)=LOWER(%s);",
                    (name, surname)
                )
                if cur.fetchone():
                    print(f"  Skipping duplicate: {name} {surname}")
                    skipped += 1
                    continue

            group_id = _ensure_group(data['group'], conn) if data['group'] else None

            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO contacts (name, surname, email, birthday, group_id)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id;""",
                    (name, surname, data['email'], data['birthday'], group_id)
                )
                cid = cur.fetchone()[0]
                for ph, pt in data['phones']:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                        (cid, ph, pt)
                    )
            inserted += 1

        conn.commit()

    print(f"  ✓ CSV import done — inserted: {inserted}, skipped: {skipped}")


# ─────────────────── 3.4  New Stored Procedures (Python callers) ──────────────

def call_add_phone(contact_name: str, phone: str, phone_type: str = 'mobile'):
    """Calls the add_phone stored procedure."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s);", (contact_name, phone, phone_type))
        conn.commit()
    print(f"  ✓ add_phone procedure called.")


def call_move_to_group(contact_name: str, group_name: str):
    """Calls the move_to_group stored procedure."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s);", (contact_name, group_name))
        conn.commit()
    print(f"  ✓ move_to_group procedure called.")


def call_search_contacts(query: str):
    """Calls the search_contacts extended function."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (query,))
            rows = cur.fetchall()
    _print_rows(rows, ["id", "name", "surname", "email", "birthday", "group", "phones"])


# ─────────────────── Display helper ───────────────────────────────────────────

def _print_rows(rows, headers):
    if not rows:
        print("  (no results)")
        return
    col_w = [len(h) for h in headers]
    str_rows = []
    for r in rows:
        sr = [str(v) if v is not None else '' for v in r]
        str_rows.append(sr)
        for i, v in enumerate(sr):
            col_w[i] = max(col_w[i], len(v))

    sep = '+' + '+'.join('-' * (w + 2) for w in col_w) + '+'
    fmt = '|' + '|'.join(f' {{:<{w}}} ' for w in col_w) + '|'

    print(sep)
    print(fmt.format(*headers))
    print(sep)
    for sr in str_rows:
        print(fmt.format(*sr))
    print(sep)
    print(f"  {len(rows)} row(s)")


# ─────────────────── Console Menu ─────────────────────────────────────────────

def menu():
    options = [
        ("─── Contacts ───────────────────────────────", None),
        ("1.  Add new contact",                         None),
        ("2.  Add phone to contact  (stored proc)",     None),
        ("3.  Move contact to group  (stored proc)",    None),
        ("─── Search & Filter ────────────────────────", None),
        ("4.  Filter by group",                         None),
        ("5.  Search by email",                         None),
        ("6.  List all contacts  (choose sort field)",  None),
        ("7.  Browse with pagination",                  None),
        ("8.  Extended pattern search  (stored func)",  None),
        ("─── Import / Export ────────────────────────", None),
        ("9.  Export to JSON",                          None),
        ("10. Import from JSON",                        None),
        ("11. Import from CSV  (extended format)",      None),
        ("─────────────────────────────────────────────", None),
        ("0.  Exit",                                    None),
    ]

    while True:
        print("\n╔══════════════════════════════════════════╗")
        print("║       PHONEBOOK — TSIS1 Extended         ║")
        print("╚══════════════════════════════════════════╝")
        for label, _ in options:
            print(f"  {label}")

        choice = input("\n  Choose: ").strip()

        if choice == '1':
            name     = input("  Name:     ").strip()
            surname  = input("  Surname:  ").strip()
            email    = input("  Email:    ").strip()
            birthday = input("  Birthday  (YYYY-MM-DD or blank): ").strip()
            group    = input("  Group     (Family/Work/Friend/Other or new): ").strip()
            cid = insert_contact(name, surname, email or None, birthday or None, group or None)
            # Optionally add phones
            while True:
                ph = input("  Add phone (blank to stop): ").strip()
                if not ph:
                    break
                pt = input("  Phone type [mobile/home/work]: ").strip() or 'mobile'
                add_phone_py(cid, ph, pt)

        elif choice == '2':
            name  = input("  Contact name: ").strip()
            phone = input("  Phone:        ").strip()
            ptype = input("  Type [mobile/home/work]: ").strip() or 'mobile'
            call_add_phone(name, phone, ptype)

        elif choice == '3':
            name  = input("  Contact name: ").strip()
            group = input("  Group name:   ").strip()
            call_move_to_group(name, group)

        elif choice == '4':
            group = input("  Group name: ").strip()
            filter_by_group(group)

        elif choice == '5':
            pattern = input("  Email pattern: ").strip()
            search_by_email(pattern)

        elif choice == '6':
            sort = input("  Sort by [name / birthday / created_at]: ").strip() or 'name'
            list_sorted(sort)

        elif choice == '7':
            try:
                size = int(input("  Page size [default 5]: ").strip() or '5')
            except ValueError:
                size = 5
            sort = input("  Sort by [name / birthday / created_at]: ").strip() or 'name'
            paginated_browse(size, sort)

        elif choice == '8':
            query = input("  Search pattern: ").strip()
            call_search_contacts(query)

        elif choice == '9':
            fn = input("  Output filename [contacts_export.json]: ").strip() or 'contacts_export.json'
            export_to_json(fn)

        elif choice == '10':
            fn = input("  JSON filename [contacts_export.json]: ").strip() or 'contacts_export.json'
            import_from_json(fn)

        elif choice == '11':
            fn = input("  CSV filename [contacts.csv]: ").strip() or 'contacts.csv'
            import_from_csv(fn)

        elif choice == '0':
            print("  Bye!")
            break
        else:
            print("  Unknown option, try again.")


if __name__ == '__main__':
    menu()
