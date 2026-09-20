import pymysql
import pymysql.cursors
from backend.config.config import Config

def get_db_connection():
    """
    Establishes and returns a database connection using PyMySQL with DictCursor
    to enable dictionary-based column access for seamless JSON responses.
    """
    connection = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
    return connection

def execute_query(sql, params=None):
    """
    Executes a SELECT query with parameterized inputs to prevent SQL Injection.
    Returns all matching rows as a list of dictionaries.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            result = cursor.fetchall()
            return result
    finally:
        conn.close()

def execute_single(sql, params=None):
    """
    Executes a SELECT query returning a single row or None.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            result = cursor.fetchone()
            return result
    finally:
        conn.close()

def execute_dml(sql, params=None):
    """
    Executes an INSERT, UPDATE, or DELETE statement with transaction commit.
    Returns a dict with 'last_id' (for INSERTs) and 'affected_rows'.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            conn.commit()
            return {'last_id': last_id, 'affected_rows': affected}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def call_stored_procedure(proc_name, params=None):
    """
    Executes a stored procedure with parameters.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc(proc_name, params or ())
            result = cursor.fetchall()
            conn.commit()
            return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def test_connection():
    """
    Quick connectivity check verifying MySQL is reachable and returns server version.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version, DATABASE() AS db_name;")
            info = cursor.fetchone()
        conn.close()
        return {'status': 'connected', 'info': info}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

