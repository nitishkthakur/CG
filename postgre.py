import psycopg2
from psycopg2 import sql

class Database:
    """
    A simple PostgreSQL database helper class for common operations.
    """

    def __init__(self, dbname, dbuser, dbpass, dbhost, dbport):
        """
        Initialize the Database object. Connects to the specified database, creating it if it does not exist.

        Args:
            dbname (str): Name of the database.
            dbuser (str): Database user.
            dbpass (str): Database password.
            dbhost (str): Database host.
            dbport (int): Database port.
        """
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbhost = dbhost
        self.dbport = dbport

        # Connect to default database to check/create target db
        self._ensure_database()
        # Connect to the target database
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            host=self.dbhost,
            port=self.dbport
        )
        self.conn.autocommit = True

    def _ensure_database(self):
        """
        Ensure the target database exists, create if not.
        """
        tmp_conn = psycopg2.connect(
            dbname='postgres',
            user=self.dbuser,
            password=self.dbpass,
            host=self.dbhost,
            port=self.dbport
        )
        tmp_conn.autocommit = True
        cur = tmp_conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.dbname,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.dbname)))
            print(f"Database '{self.dbname}' did not exist. Created new database.")
        else:
            print(f"Database '{self.dbname}' already exists.")
        cur.close()
        tmp_conn.close()

    def create_table(self, table_name, columns):
        """
        Create a table with the given name and columns.

        Args:
            table_name (str): Name of the table.
            columns (list of tuples): Each tuple is (column_name, column_type).
        """
        with self.conn.cursor() as cur:
            cols = ', '.join([f"{name} {ctype}" for name, ctype in columns])
            cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                sql.Identifier(table_name),
                sql.SQL(cols)
            ))
            # Check if table was created or already existed
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = %s
                )
            """, (table_name,))
            exists = cur.fetchone()[0]
            if exists:
                # Table exists after the command, but we don't know if it existed before.
                # So, check if table is empty (newly created) or has columns (already existed)
                cur.execute("""
                    SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                """, (table_name,))
                col_count = cur.fetchone()[0]
                if col_count == len(columns):
                    print(f"Table '{table_name}' did not exist. Created new table.")
                else:
                    print(f"Table '{table_name}' already exists.")
            else:
                print(f"Table '{table_name}' was not created due to an unknown error.")

    def insert(self, table_name, data):
        """
        Insert data into a table.

        Args:
            table_name (str): Name of the table.
            data (list of dict or list of tuple): Data to insert.
        """
        with self.conn.cursor() as cur:
            if isinstance(data, dict):
                data = [data]
            if isinstance(data[0], dict):
                columns = data[0].keys()
                values = [[row[col] for col in columns] for row in data]
            else:
                # Assume list of tuples, need column names
                raise ValueError("Insert data must be a list of dictionaries with column names as keys.")
            cols_sql = sql.SQL(', ').join(map(sql.Identifier, columns))
            vals_sql = sql.SQL(', ').join(sql.Placeholder() * len(columns))
            insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                cols_sql,
                vals_sql
            )
            for row in values:
                cur.execute(insert_sql, row)

    def select(self, table_name, columns, where=None):
        """
        Select data from a table.

        Args:
            table_name (str): Name of the table.
            columns (list): List of column names to select.
            where (dict, optional): WHERE clause as {column: value}.

        Returns:
            list of tuples: Query results.
        """
        with self.conn.cursor() as cur:
            cols_sql = sql.SQL(', ').join(map(sql.Identifier, columns))
            query = sql.SQL("SELECT {} FROM {}").format(
                cols_sql,
                sql.Identifier(table_name)
            )
            params = []
            if where:
                where_clause = sql.SQL(' AND ').join(
                    sql.Composed([sql.Identifier(k), sql.SQL('=%s')]) for k in where.keys()
                )
                query += sql.SQL(" WHERE ") + where_clause
                params = list(where.values())
            cur.execute(query, params)
            return cur.fetchall()

    def update(self, table_name, data, where):
        """
        Update rows in a table.

        Args:
            table_name (str): Name of the table.
            data (dict): Columns and new values.
            where (dict): WHERE clause as {column: value}.
        """
        with self.conn.cursor() as cur:
            set_clause = sql.SQL(', ').join(
                sql.Composed([sql.Identifier(k), sql.SQL('=%s')]) for k in data.keys()
            )
            where_clause = sql.SQL(' AND ').join(
                sql.Composed([sql.Identifier(k), sql.SQL('=%s')]) for k in where.keys()
            )
            query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
                sql.Identifier(table_name),
                set_clause,
                where_clause
            )
            params = list(data.values()) + list(where.values())
            cur.execute(query, params)

    def delete(self, table_name, where):
        """
        Delete rows from a table.

        Args:
            table_name (str): Name of the table.
            where (dict): WHERE clause as {column: value}.
        """
        with self.conn.cursor() as cur:
            where_clause = sql.SQL(' AND ').join(
                sql.Composed([sql.Identifier(k), sql.SQL('=%s')]) for k in where.keys()
            )
            query = sql.SQL("DELETE FROM {} WHERE {}").format(
                sql.Identifier(table_name),
                where_clause
            )
            params = list(where.values())
            cur.execute(query, params)

    def drop_table(self, table_name):
        """
        Drop a table from the database.

        Args:
            table_name (str): Name of the table.
        """
        with self.conn.cursor() as cur:
            cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(
                sql.Identifier(table_name)
            ))


if __name__ == "__main__":
    # Example usage
    db = Database(
        dbname='cg_db2',
        dbuser='postgres',
        dbpass='postgres',
        dbhost='localhost',
        dbport=5432
    )

    # List of common data types which can be used in postgres schema
    common_data_types = [
        'SERIAL', 'BIGSERIAL', 'SMALLSERIAL', 'INTEGER', 'BIGINT', 'SMALLINT',
        'DECIMAL', 'NUMERIC', 'REAL', 'DOUBLE PRECISION', 'MONEY',
        'CHARACTER VARYING', 'VARCHAR', 'CHARACTER', 'CHAR', 'TEXT',
        'BOOLEAN', 'DATE', 'TIME', 'TIMESTAMP', 'TIMESTAMPTZ',
        'INTERVAL', 'UUID'
    ]

    # Print common data types
    print("Common PostgreSQL Data Types:")
    for dtype in common_data_types:
        print(dtype)
        
    # Create a table
    db.create_table(
        'test_table',
        [
            ('id', 'SERIAL PRIMARY KEY'),
            ('name', 'VARCHAR(100)'),
            ('value', 'INTEGER')
        ]
    )

    # Insert 3 items to the table
    db.insert('test_table', {'name': 'Item 1', 'value': 10})
    db.insert('test_table', {'name': 'Item 2', 'value': 20})
    db.insert('test_table', {'name': 'Item 3', 'value': 30})
