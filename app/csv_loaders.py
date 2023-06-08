import pandas as pd
import sqlite3


def load_csv_to_sqlite(file_path, table_name):
    # Load data file
    df = pd.read_csv(file_path)

    # Strip leading and trailing spaces from column names
    df.columns = df.columns.str.strip()

    # Connect to an SQLite database
    connection = sqlite3.connect('data/demo.db')

    # Load data file to SQLite
    # if_exists options are: 'fail', 'replace', 'append'
    # df.to_sql(table_name, connection, if_exists='replace')

    # Optional: close the database connection when you're done
    # connection.close()

    # Create a cursor object
    cursor = connection.cursor()

    # Drop the table if it exists
    cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

     # Load data file to SQLite
    # if_exists options are: 'fail', 'replace', 'append'
    df.to_sql(table_name, connection, if_exists='replace')

    # Commit the transaction
    connection.commit()


    # Close the cursor
    # cursor.close()

    # Return the connection instead of closing it
    return connection