import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from typing import List, Any

load_dotenv()

class DatabaseAdapter:
    def __init__(self) -> None:
        self.connection = None

    def connect(self) -> None:
        try:
            self.connection = psycopg2.connect(
                dbname=os.getenv("DBNAME"),
                user="postgres",
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),  
                port=os.getenv("DB_PORT")
            )
            print("Соединение с базой данных установлено.")
        except psycopg2.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise
    def initialize_tables(self) -> None:
        table_definitions = {
            "reverse": """
                CREATE TABLE IF NOT EXISTS reverse  (
                    id VARCHAR(200) PRIMARY KEY,
                    who VARCHAR(1000),
                    quality VARCHAR(1000),
                    what_was_he_doing VARCHAR(1000),
                    reaction VARCHAR(1000)
                );
            """
        }
        with self.connection.cursor() as cursor:
            for table_name, create_query in table_definitions.items():
                cursor.execute(create_query)
                print(f"Таблица '{table_name}' проверена или создана.")
            self.connection.commit()

        # with self.connection.cursor() as cursor:
        #     for table_name, full_sql in table_definitions.items():
        #         # Разделим на отдельные команды, если в одном блоке DROP + CREATE
        #         for statement in full_sql.strip().split(";"):
        #             if statement.strip():
        #                 cursor.execute(statement.strip() + ";")
        #         print(f"Таблица '{table_name}' пересоздана.")
        #     self.connection.commit()

    def get_all(self, table_name: str) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {table_name};")
            return cursor.fetchall()

    def get_by_id(self, table_name: str, id: str | int) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s;", (id,))
            return cursor.fetchall()
        
    def insert_or_update(self, table: str, data: dict):
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        updates = ', '.join([f"{k}=EXCLUDED.{k}" for k in data if k != "id"])

        sql = f"""
        INSERT INTO {table} ({keys}) VALUES ({values})
        ON CONFLICT (id) DO UPDATE SET {updates};
        """

        with self.connection.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            self.connection.commit()

    def get_by_value(
        self,
        table_name: str,
        parameter: str,
        parameter_value: Any,
    ) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"SELECT * FROM {table_name} WHERE {parameter} = %s;"
            cursor.execute(query, (parameter_value,))
            return cursor.fetchall()

    def insert(self, table_name: str, insert_dict: dict) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            columns = ', '.join(insert_dict.keys())
            values = ', '.join(['%s'] * len(insert_dict))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values}) RETURNING *;"
            cursor.execute(query, tuple(insert_dict.values()))
            self.connection.commit()
            return cursor.fetchall()

    def update(self, table_name: str, update_dict: dict, id: int) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            set_clause = ', '.join([f"{key} = %s" for key in update_dict.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s RETURNING *;"
            cursor.execute(query, tuple(update_dict.values()) + (id,))
            self.connection.commit()
            return cursor.fetchall()

    def delete(self, table_name: str, id: int) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"DELETE FROM {table_name} WHERE id = %s RETURNING *;"
            cursor.execute(query, (id,))
            self.connection.commit()
            return cursor.fetchall()

    def execute_with_request(self, request):
        with self.connection.cursor() as cursor:
                cursor.execute(request)
                self.connection.commit()
                if cursor.description:
                    rows = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    return [dict(zip(column_names, row)) for row in rows]
                return None

    def delete_by_value(
        self,
        table_name: str,
        parameter: str,
        parameter_value: Any,
    ) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"DELETE FROM {table_name} WHERE {parameter} = %s RETURNING *;"
            cursor.execute(query, (parameter_value,))
            self.connection.commit()
            return cursor.fetchall()
        
    def update_by_value(
        self,
        table_name: str,
        update_dict: dict,
        parameter: Any,
        value: Any
    ) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            set_clause = ', '.join([f"{key} = %s" for key in update_dict.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {parameter} = %s RETURNING *;"
            cursor.execute(query, tuple(update_dict.values()) + (value,))
            self.connection.commit()
    
    def truncate_table(self, table_name: str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {table_name};")
            self.connection.commit()