"""
database.py — Couche Données (SQLite)
Simule une base MySQL/PostgreSQL
"""

import sqlite3
import pandas as pd
import os
import streamlit as st

def get_db_connection():
    """Retourne une connexion à la base SQLite"""
    base = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base, '..', 'database', 'acremac.db')
    return sqlite3.connect(db_path)

@st.cache_data
def charger_clients_depuis_db():
    """Extrait les clients depuis la base SQLite"""
    conn = get_db_connection()
    query = "SELECT * FROM clients"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def compter_clients():
    """Compte le nombre total de clients"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clients")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def filtrer_clients(pays=None, secteur=None, score_min=None, score_max=None):
    """Filtre les clients avec des requêtes SQL dynamiques"""
    conn = get_db_connection()
    
    query = "SELECT * FROM clients WHERE 1=1"
    params = []
    
    if pays and pays != "Tous":
        query += " AND country = ?"
        params.append(pays)
    
    if secteur and secteur != "Tous":
        query += " AND sector = ?"
        params.append(secteur)
    
    if score_min is not None:
        query += " AND solvency_score >= ?"
        params.append(score_min)
    
    if score_max is not None:
        query += " AND solvency_score <= ?"
        params.append(score_max)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

@st.cache_data
def get_stats_pays():
    """Statistiques par pays (SQL GROUP BY)"""
    conn = get_db_connection()
    query = """
        SELECT 
            country,
            COUNT(*) as nb_clients,
            AVG(solvency_score) as score_moyen,
            MIN(solvency_score) as score_min,
            MAX(solvency_score) as score_max
        FROM clients
        GROUP BY country
        ORDER BY score_moyen DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def get_stats_secteur():
    """Statistiques par secteur (SQL GROUP BY)"""
    conn = get_db_connection()
    query = """
        SELECT 
            sector,
            COUNT(*) as nb_clients,
            AVG(solvency_score) as score_moyen,
            MIN(solvency_score) as score_min,
            MAX(solvency_score) as score_max
        FROM clients
        GROUP BY sector
        ORDER BY score_moyen DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def get_stats_categorie():
    """Statistiques par catégorie de score (SQL CASE WHEN)"""
    conn = get_db_connection()
    query = """
        SELECT 
            CASE 
                WHEN solvency_score >= 680 THEN 'Excellent'
                WHEN solvency_score >= 620 THEN 'Bon'
                WHEN solvency_score >= 560 THEN 'Moyen'
                ELSE 'Risqué'
            END as categorie,
            COUNT(*) as nb_clients,
            AVG(solvency_score) as score_moyen,
            MIN(solvency_score) as score_min,
            MAX(solvency_score) as score_max
        FROM clients
        GROUP BY categorie
        ORDER BY score_moyen DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def charger_toutes_donnees():
    """Charge toutes les données de la base"""
    df_brut = charger_clients_depuis_db()
    return df_brut