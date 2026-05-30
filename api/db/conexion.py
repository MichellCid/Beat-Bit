import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def conexion():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "beatandbit_dwh"),
        user=os.getenv("DB_USER", "usuario"),
        password=os.getenv("DB_PASSWORD", "1234")
    )