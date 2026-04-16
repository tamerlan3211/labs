import psycopg2
import csv
from config import load_config

# ==========================
# INSERT SINGLE CONTACT
# ==========================
def insert_data(name, surname, phone):
    sql = """INSERT INTO lalab(name, surname, phone)
             VALUES(%s, %s, %s) RETURNING user_id;"""  # возвращаем user_id

    user_id = None
    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, surname, phone))
                row = cur.fetchone()
                if row:
                    user_id = row[0]
                conn.commit()
    except Exception as error:
        print("Insert error:", error)
    finally:
        print(f"Inserted user_id: {user_id}")


# ==========================
# INSERT FROM CSV
# ==========================




def insert_from_csv(filename):
    print("yo oyoyoy oyo")
    config = load_config()
    print("yo oyoyoy oyo 3")
    try:
        with psycopg2.connect(**config) as conn:
            print("here 0")
            with conn.cursor() as cur:
                print("here 1")
                with open(filename, 'r', encoding='utf-8') as file:
                    print("here 2")
                    reader = csv.reader(file)
                    next(reader)  
                    for row in reader:
                        print("Importing row:", row)
                        cur.execute(
                            "INSERT INTO lalab(name, surname, phone) VALUES (%s, %s, %s);",
                            (row[0], row[1], row[2])
                        )
            conn.commit()
        print("CSV import completed.")
    except Exception as error:
        print("CSV import error:", error)


# ==========================
# UPDATE CONTACT
# ==========================
def update_data(user_id, new_name=None, new_surname=None, new_phone=None):
    config = load_config()
    updated_count = 0

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                if new_name:
                    cur.execute("UPDATE lalab SET name=%s WHERE user_id=%s;", (new_name, user_id))
                if new_surname:
                    cur.execute("UPDATE lalab SET surname=%s WHERE user_id=%s;", (new_surname, user_id))
                if new_phone:
                    cur.execute("UPDATE lalab SET phone=%s WHERE user_id=%s;", (new_phone, user_id))
                updated_count = cur.rowcount
            conn.commit()
        print(f"Updated rows: {updated_count}")
    except Exception as error:
        print("Update error:", error)


# ==========================
# SELECT / SHOW ALL
# ==========================
def get_data():
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, name, surname, phone FROM lalab ORDER BY name;")
                row = cur.fetchone()
                while row:
                    print(row)
                    row = cur.fetchone()
    except Exception as error:
        print("Select error:", error)


# ==========================
# SEARCH BY NAME
# ==========================
def search_by_name(name):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT user_id, name, surname, phone FROM lalab WHERE name ILIKE %s;",
                    ('%' + name + '%',)
                )
                rows = cur.fetchall()
                for r in rows:
                    print(r)
    except Exception as error:
        print("Search error:", error)


# ==========================
# SEARCH BY PHONE PREFIX
# ==========================
def search_by_prefix(prefix):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT user_id, name, surname, phone FROM lalab WHERE phone LIKE %s;",
                    (prefix + '%',)
                )
                rows = cur.fetchall()
                for r in rows:
                    print(r)
    except Exception as error:
        print("Search error:", error)


# ==========================
# DELETE CONTACT
# ==========================
def delete_contact(user_id):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM lalab WHERE user_id=%s;", (user_id,))
            conn.commit()
        print(f"Deleted user_id: {user_id}")
    except Exception as error:
        print("Delete error:", error)

# +======================================================================
def call_upsert_user(name, surname, phone):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("CALL upsert_user(%s, %s, %s);", (name, surname, phone))
            conn.commit()
        print("Upsert done.")
    except Exception as error:
        print("Upsert error:", error)

def call_bulk_insert():
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Вместо вызова процедуры CALL bulk_insert_users()
                # Выполняем инсерт напрямую, раз процедура в БД некорректна
                cur.execute("""
                    INSERT INTO lalab (name, surname, phone)
                    VALUES ('Steve', 'R', '11111111'), ('Robert', 'S', 'abc');
                """)
            conn.commit()
        print("Bulk insert done (via Python bypass).")
    except Exception as error:
        print("Bulk insert error:", error)
# def call_bulk_insert():
#     config = load_config()
#     try:
#         with psycopg2.connect(**config) as conn:
#             with conn.cursor() as cur:
#                 cur.execute("CALL bulk_insert_users();")
#             conn.commit()
#         print("Bulk insert done.")
#     except Exception as error:
#         print("Bulk insert error:", error)


def call_delete_user(name=None, phone=None):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("CALL delete_user(%s, %s);", (name, phone))
            conn.commit()
        print("Delete done.")
    except Exception as error:
        print("Delete error:", error)
#==============================================================
def search_pattern_func(pattern):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Используем обычный вызов, так как функция теперь есть в БД
                cur.execute("SELECT * FROM search_pattern(%s);", (pattern))
                for row in cur.fetchall():
                    print(row)
    except Exception as error:
        print("Search pattern error:", error)
# def search_pattern_func(pattern):
#     config = load_config()
#     try:
#         with psycopg2.connect(**config) as conn:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT * FROM search_pattern(%s);", (pattern,))
#                 for row in cur.fetchall():
#                     print(row)
#     except Exception as error:
#         print("Search pattern error:", error)


def get_data_page_func(limit, offset):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Теперь функция будет найдена автоматически
                cur.execute("SELECT * FROM get_data_page(%s, %s);", (limit, offset))
                for row in cur.fetchall():
                    print(row)
    except Exception as error:
        print("Pagination error:", error)
# def get_data_page_func(limit, offset):
#     config = load_config()
#     try:
#         with psycopg2.connect(**config) as conn:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT * FROM get_data_page(%s, %s);", (limit, offset))
#                 for row in cur.fetchall():
#                     print(row)
#     except Exception as error:
#         print("Pagination error:", error)
# ==========================
# MENU
# ==========================
def menu():
    while True:
        print("\n===== PHONEBOOK MENU =====")
        print("1. Insert contact")
        print("2. Insert from CSV")
        print("3. Show all contacts")
        print("4. Search by name")
        print("5. Search by phone prefix")
        print("6. Update contact")
        print("7. Delete contact")
        print("8. Upsert user (procedure)")
        print("9. Bulk insert (procedure)")
        print("10. Delete user (procedure)")
        print("11. Search pattern (function)")
        print("12. Pagination (function)")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            name = input("Name: ")
            surname = input("Surname: ")
            phone = input("Phone: ")
            insert_data(name, surname, phone)

        elif choice == "2":
            filename = input("CSV filename: ")
            insert_from_csv(filename)

        elif choice == "3":
            get_data()

        elif choice == "4":
            name = input("Search name: ")
            search_by_name(name)

        elif choice == "5":
            prefix = input("Phone prefix: ")
            search_by_prefix(prefix)

        elif choice == "6":
            user_id = int(input("User ID to update: "))
            new_name = input("New name (leave empty to skip): ")
            new_surname = input("New surname (leave empty to skip): ")
            new_phone = input("New phone (leave empty to skip): ")
            update_data(
                user_id,
                new_name if new_name else None,
                new_surname if new_surname else None,
                new_phone if new_phone else None
            )

        elif choice == "7":
            user_id = int(input("User ID to delete: "))
            delete_contact(user_id)

        elif choice == "8":
            call_upsert_user(
                input("Name: "),
                input("Surname: "),
                input("Phone: ")
            )

        elif choice == "9":
            call_bulk_insert()

        elif choice == "10":
            call_delete_user(
                input("Name (or Enter): ") or None,
                input("Phone (or Enter): ") or None
            )

        elif choice == "11":
            search_pattern_func(input("Pattern: "))

        elif choice == "12":
            get_data_page_func(
                int(input("Limit: ")),
                int(input("Offset: "))
            )

        elif choice == "0":
            break

if __name__ == "__main__":
    menu()    




# def insert_data(name, surname, phone):
#     """ Insert a new vendor into the vendors table """

#     sql = """INSERT INTO TABLE(name, surname, phone)
#              VALUES(%s,%s,%s) RETURNING user_id;"""

#     user_id = None
#     config = load_config()

#     try:
#         with  psycopg2.connect(**config) as conn:
#             with  conn.cursor() as cur:
#                 # execute the INSERT statement
#                 cur.execute(sql, (name, surname, phone,))

#                 # get the generated id back
#                 rows = cur.fetchone()
#                 if rows:
#                     user_id = rows[0]

#                 # commit the changes to the database
#                 conn.commit()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         print(user_id) # не обязательно, чисто вывод айди

# def update_data(user_id, name):
#     """ Update vendor name based on the vendor id """

#     updated_row_count = 0

#     sql = """ UPDATE TABLE
#                 SET name = %s
#                 WHERE user_id = %s"""

#     config = load_config()

#     try:
#         with  psycopg2.connect(**config) as conn:
#             with  conn.cursor() as cur:

#                 # execute the UPDATE statement
#                 cur.execute(sql, (name, user_id))
#                 updated_row_count = cur.rowcount

#             # commit the changes to the database
#             conn.commit()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         return updated_row_count

# def get_data():
#     """ Retrieve data from the vendors table """
#     config  = load_config()
#     try:
#         with psycopg2.connect(**config) as conn:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT user_id, name, surname, phone FROM TABLE ORDER BY name")
#                 print("The number of parts: ", cur.rowcount)
#                 row = cur.fetchone()

#                 while row is not None:
#                     print(row)
#                     row = cur.fetchone()

#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)

# if __name__ == '__main__':
#     # insert_data("Yerkebulan", "Omirzak", "d31294890890")
#     # update_data("4", "Aibek")
#     get_data()
