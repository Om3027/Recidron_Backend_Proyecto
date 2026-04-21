import os
import pymysql
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(dotenv_path='.env.dev')

DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_PORT = os.getenv('DATABASE_PORT')

class CursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor
        
    def execute(self, query, args=None):
        self._cursor.execute(query, args)
        return self
        
    def fetchone(self):
        return self._cursor.fetchone()
        
    def fetchall(self):
        return self._cursor.fetchall()
        
    @property
    def lastrowid(self):
        return self._cursor.lastrowid

class MySQLConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def close(self):
        self._conn.close()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def execute(self, query, args=None):
        cursor = self._conn.cursor()
        cursor.execute(query, args)
        return CursorWrapper(cursor)

    def cursor(self):
        return CursorWrapper(self._conn.cursor())

def get_connection():
    """
    Crea y retorna una conexión a la base de datos de MySQL.
    """
    conn = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        port=int(DATABASE_PORT),
        db=DATABASE_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    return MySQLConnectionWrapper(conn)
