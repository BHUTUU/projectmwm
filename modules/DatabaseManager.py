import mysql.connector

class DatabaseManager:
    def __init__(self, host, user, password, database_name):
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database_name  # Select the database during connection
        }
        self.database_name = database_name
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.connection = mysql.connector.connect(**self.db_config)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    def check_table_exists(self, table_name):
        check_table_query = f"SHOW TABLES LIKE '{table_name}'"
        self.cursor.execute(check_table_query)
        existing_tables = self.cursor.fetchall()
        return bool(existing_tables)
    
    def check_database_exists(self):
        check_db_query = f"SHOW DATABASES LIKE '{self.database_name}'"
        self.cursor.execute(check_db_query)
        existing_databases = self.cursor.fetchall()
        return bool(existing_databases)

    def create_database(self):
        create_db_query = f"CREATE DATABASE {self.database_name}"
        self.cursor.execute(create_db_query)
        print(f"Database '{self.database_name}' created successfully.")

    def create_table(self, table_name, columns):
        column_definitions = ', '.join(columns)
        create_table_query = f"CREATE TABLE {table_name} ({column_definitions})"
        self.cursor.execute(create_table_query)
        return True
        # print(f"Table '{table_name}' created successfully.")
    def delete_table(self, table_name):
        if self.check_table_exists(table_name):
            delete_table_query = f"DROP TABLE {table_name}"
            self.cursor.execute(delete_table_query)
            return True
        else:
            return False
    def create_columns(self, table_name, columns):
        if self.check_table_exists(table_name):
            alter_table_query = f"ALTER TABLE {table_name} ADD COLUMN {', '.join(columns)}"
            self.cursor.execute(alter_table_query)
            return True
        else:
            return False
    def add_data(self, table_name, column_names, values):
        if self.check_table_exists(table_name):
            placeholders = ', '.join(['%s'] * len(column_names))
            insert_data_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
            self.cursor.execute(insert_data_query, values)
            self.connection.commit()
            return True
        else:
            return False
    def get_value(self, table_name, column_name):
        select_query = f"SELECT {column_name} FROM {table_name}"
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        if result:
            return result
        return None
    def get_value_row(self, table_name, column_name, value):
        select_query = f"SELECT * from {table_name} WHERE {column_name} = '{value}'"
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        if result:
            return result
        return None
    def alter_value(self, table_name, column_name, value, row_id):
        alter_query = f"UPDATE {table_name} SET {column_name} = %s WHERE id = %s"
        self.cursor.execute(alter_query, (value, row_id))
        self.connection.commit()
        return self.cursor.rowcount  # Returns the number of rows affected by the UPDATE statement

    def delete_data(self, table_name, column_name, correspondingValue): # This function is used to delete row by a specific column name and its value if match found.
        select_query = f"DELETE FROM {table_name} WHERE {column_name}='{correspondingValue}'"
        self.cursor.execute(select_query)
        self.connection.commit()
        return True

    def execute_query(self, query):
        self.cursor.execute(query)
        self.connection.commit()