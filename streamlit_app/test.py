import sqlite3
import pandas as pd
import os

base = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base, '..', 'database', 'acremac.db')

print("DB =", db_path)

conn = sqlite3.connect(db_path)

df = pd.read_sql_query("""
SELECT *
FROM clients
WHERE client_id='C100200'
""", conn)

print(df.T)

conn.close()