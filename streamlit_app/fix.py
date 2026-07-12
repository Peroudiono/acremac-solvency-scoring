import sqlite3
import os

base = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base, '..', 'database', 'acremac.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
UPDATE clients
SET loan_duration_months = 12
WHERE client_id = 'C100200'
""")

conn.commit()
conn.close()

print("Correction effectuée.")