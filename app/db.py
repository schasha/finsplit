import psycopg2
import psycopg2.extras

from .config import Config


def get_connection():
    return psycopg2.connect(
        host=Config.DB_HOST,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT,
    )


def query(sql, params=None, fetch=True):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params or ())
    rows = cur.fetchall() if fetch else None
    conn.commit()
    cur.close()
    conn.close()
    return rows

# CORRIGIDO: execute_raw() removido. Toda query agora passa por query() com
# parâmetros (%s), eliminando a concatenação que gerava SQL Injection.
