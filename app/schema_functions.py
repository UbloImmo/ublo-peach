import sqlite3


def print_db_schema(db_name, conn, st):

    # Get a list of all tables
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    tables = [table[0] for table in tables]

    for table in tables:
        st.write(f"Table: {table}")

        # Get all columns for this table
        cursor = conn.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        st.write("Columns:")
        for column in columns:
            st.write(column)

        # Get all foreign keys for this table
        cursor = conn.execute(f"PRAGMA foreign_key_list({table});")
        foreign_keys = cursor.fetchall()
        st.write("Foreign Keys:")
        for foreign_key in foreign_keys:
            st.write(foreign_key)

        st.write()

