import psycopg2
import os

def obtener_conexion_bd():
    try:
        conn = psycopg2.connect(
            host="postgres",
            database=os.getenv("POSTGRES_DB", "beatandbit_dwh"),
            user=os.getenv("POSTGRES_USER", "usuario"),
            password=os.getenv("POSTGRES_PASSWORD", "1234")
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None