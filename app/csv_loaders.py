import pandas as pd
import sqlite3

def load_csv_to_sqlite(file_path, table_name):
    # Load data file
    df = pd.read_csv(file_path)

    # Strip leading and trailing spaces from column names
    df.columns = df.columns.str.strip()

    # Create / connect to a SQLite database
    connection = sqlite3.connect('demo.db')

    # Load data file to SQLite
    # if_exists options are: 'fail', 'replace', 'append'
    df.to_sql(table_name, connection, if_exists='replace')

    # Optional: close the database connection when you're done
    connection.close()