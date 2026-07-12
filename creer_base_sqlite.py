"""
creer_base_sqlite.py
Convertit le fichier Excel ACREMAC en base SQLite
Auteur : Diono dit Boubacar PEROU
"""

import sqlite3
import pandas as pd
import os

# ── Configuration ──────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, 'data', 'Dataset_scoring_solvabilite_ACREMAC.xlsx')
DB_PATH = os.path.join(BASE, 'database', 'acremac.db')

# ── Création du dossier database s'il n'existe pas ──────────────────────────
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ── Chargement du fichier Excel ──────────────────────────────────────────────
print(f"📁 Chargement du fichier : {DATA_PATH}")
df = pd.read_excel(DATA_PATH)

print(f"📊 {len(df)} lignes × {len(df.columns)} colonnes chargées")

# ── Création de la base SQLite ──────────────────────────────────────────────
print(f"💾 Création de la base : {DB_PATH}")

# Connexion à la base (crée le fichier s'il n'existe pas)
conn = sqlite3.connect(DB_PATH)

# Écriture du DataFrame dans la table 'clients'
df.to_sql('clients', conn, if_exists='replace', index=False)

# ── Vérification ──────────────────────────────────────────────────────────────
print("\n🔍 Vérification :")
cursor = conn.cursor()

# Compter les enregistrements
cursor.execute("SELECT COUNT(*) FROM clients")
count = cursor.fetchone()[0]
print(f"   ✅ {count} enregistrements dans la table 'clients'")

# Afficher la structure de la table
cursor.execute("PRAGMA table_info(clients)")
columns = cursor.fetchall()
print(f"   ✅ {len(columns)} colonnes : {', '.join([col[1] for col in columns])}")

# Afficher les 5 premiers clients
print("\n📋 Aperçu des 5 premiers clients :")
cursor.execute("SELECT client_id, client_type, country, sector FROM clients LIMIT 5")
for row in cursor.fetchall():
    print(f"   {row}")

# ── Fermeture de la connexion ────────────────────────────────────────────────
conn.close()

print(f"\n✅ Base SQLite créée avec succès : {DB_PATH}")
print("📌 Utilise-la maintenant dans ton application Streamlit !")