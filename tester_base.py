"""
tester_base.py
Teste la connexion à la base SQLite
"""

import sqlite3
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, 'database', 'acremac.db')

def tester_connexion():
    print(f"🔍 Connexion à la base : {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Compter les clients
        cursor.execute("SELECT COUNT(*) FROM clients")
        count = cursor.fetchone()[0]
        print(f"   ✅ {count} clients")
        
        # 2. Compter par pays
        cursor.execute("""
            SELECT country, COUNT(*) as nb 
            FROM clients 
            GROUP BY country 
            ORDER BY nb DESC
        """)
        print("\n   📊 Répartition par pays :")
        for row in cursor.fetchall():
            print(f"      {row[0]} : {row[1]} clients")
        
        # 3. Score moyen par catégorie
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN solvency_score >= 680 THEN 'Excellent'
                    WHEN solvency_score >= 620 THEN 'Bon'
                    WHEN solvency_score >= 560 THEN 'Moyen'
                    ELSE 'Risqué'
                END as categorie,
                COUNT(*) as nb,
                AVG(solvency_score) as score_moyen
            FROM clients
            GROUP BY categorie
            ORDER BY score_moyen DESC
        """)
        print("\n   📊 Répartition par catégorie :")
        for row in cursor.fetchall():
            print(f"      {row[0]} : {row[1]} clients (moy. {row[2]:.0f})")
        
        conn.close()
        print("\n✅ Base SQLite testée avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    tester_connexion()