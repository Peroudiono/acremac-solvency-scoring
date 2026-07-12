"""
ACREMAC — Moteur de Scoring de Solvabilité
Application Streamlit — Architecture 4 couches
Auteur : Diono dit Boubacar PEROU
"""

import streamlit as st
import hashlib
import os
import base64
import sqlite3
import pandas as pd
import numpy as np
import pickle
import json
import shap
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter



















# ============================================================
# 1. AUTHENTIFICATION
# ============================================================

try:
    UTILISATEURS = st.secrets["UTILISATEURS"]
except Exception:
    UTILISATEURS = {
        "admin": {
            "mot_de_passe_hache": "974832e8cba6623daedfc1275bb2d5fb647432223ea8897a1e8c838a72012bd1",
            "nom": "Administrateur",
            "role": "admin"
        },
        "analyste": {
            "mot_de_passe_hache": "3f78c2afd2f5c3a291d8ce5988a5d6d3acacfd566742d8cdbb7bc2a6b30254ba",
            "nom": "Analyste ACREMAC",
            "role": "analyste"
        },
        "boubacar": {
            "mot_de_passe_hache": "2fe1fc7b4e72a70872a050d3415afd75a4b258fd951d423dc94573a6594c2200",
            "nom": "Diono dit Boubacar PEROU",
            "role": "createur"
        }
    }

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG_IMAGE = os.path.join(BASE_DIR, "images", "arriere.png")


def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return ""


def verifier_authentification():
    """Vérifie si l'utilisateur est authentifié"""

    if st.session_state.get("authentifie", False):
        return True

    bg_base64 = get_image_base64(BG_IMAGE)

    # Arriere-plan injecte en f-string separe pour interpoler bg_base64
    st.markdown(
        f'<style>.stApp {{'
        f'    background-image:url("{bg_base64}") !important;'
        f'    background-repeat:no-repeat !important;'
        f'    background-position:center !important;'
        f'    background-size:contain !important;'
        f'    background-color:white !important;'
        f'    height:100vh !important;'
        f'}}</style>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<style>'
        '.stApp {'
        '    background-color:white !important;'
        '}'
        '#MainMenu,footer,header,'
        '[data-testid="stSidebar"],'
        '[data-testid="stHeader"]{'
        '    display:none !important;'
        '}'
        '.lc-card{'
        '    background:rgba(255,255,255,0.97);'
        '    padding:0 0 22px 0;'
        '    border-radius:14px;'
        '    box-shadow:0 2px 8px rgba(0,0,0,.06),0 12px 32px rgba(0,0,0,.10);'
        '    border:0.5px solid rgba(0,0,0,.08);'
        '    margin-top:160px;'
        '    overflow:hidden;'
        '}'
        '.lc-bar{'
        '    height:4px;'
        '    background:linear-gradient(90deg,#173A7A 0%,#1d52a8 55%,#D8A03F 100%);'
        '}'
        '.lc-body{'
        '    padding:22px 24px 0 24px;'
        '}'
        '.lc-logo-row{'
        '    display:flex;'
        '    align-items:center;'
        '    gap:11px;'
        '    margin-bottom:18px;'
        '}'
        '.lc-logo-mark{'
        '    width:38px;height:38px;'
        '    background:linear-gradient(135deg,#173A7A 0%,#D8A03F 100%);'
        '    border-radius:9px;'
        '    display:flex;align-items:center;justify-content:center;'
        '    flex-shrink:0;'
        '}'
        '.lc-logo-mark svg{width:19px;height:19px;}'
        '.lc-name{font-size:15px;font-weight:700;color:#0d1f3c;letter-spacing:.4px;line-height:1.2;margin:0;}'
        '.lc-sub{font-size:10px;color:#94a3b8;letter-spacing:.5px;text-transform:uppercase;margin:0;}'
        '.lc-divider{height:0.5px;background:#e2e8f0;margin-bottom:18px;}'
        '.lc-h2{color:#0d1f3c !important;font-size:19px !important;font-weight:700 !important;margin:0 0 3px 0 !important;}'
        '.lc-desc{color:#64748b;font-size:12.5px;margin:0 0 0 0;}'
        '.lc-footer{'
        '    margin:14px 24px 0 24px;'
        '    padding-top:14px;'
        '    border-top:0.5px solid #f1f5f9;'
        '    text-align:center;'
        '    font-size:11px;'
        '    color:#94a3b8;'
        '    display:flex;align-items:center;justify-content:center;gap:7px;'
        '}'
        '.lc-dot{width:3px;height:3px;background:#cbd5e1;border-radius:50%;display:inline-block;}'
        
        '[data-testid="stForm"] input[type="text"],'
        '[data-testid="stForm"] input[type="password"]{'
        '    border:0.5px solid #cbd5e1 !important;'
        '    border-radius:8px !important;'
        '    background:#f8fafc !important;'
        '    height:40px !important;'
        '    font-size:14px !important;'
        '    color:#0d1f3c !important;'
        '    box-shadow:none !important;'
        '    transition:border-color .15s,box-shadow .15s !important;'
        '}'
        '[data-testid="stForm"] input[type="text"]:focus,'
        '[data-testid="stForm"] input[type="password"]:focus{'
        '    border-color:#173A7A !important;'
        '    background:#ffffff !important;'
        '    box-shadow:0 0 0 3px rgba(23,58,122,.10) !important;'
        '    outline:none !important;'
        '}'
        
        '[data-testid="stForm"] [data-testid="InputInstructions"]{'
        '    display:none !important;'
        '}'
        '[data-testid="stForm"] button[kind="icon"],'
        '[data-testid="stForm"] button[aria-label="Toggle password visibility"]{'
        '    background:transparent !important;'
        '    border:none !important;'
        '    box-shadow:none !important;'
        '    color:#94a3b8 !important;'
        '    padding:0 8px !important;'
        '    min-width:unset !important;'
        '    height:40px !important;'
        '    margin-top:0 !important;'
        '}'
        '[data-testid="stForm"] button[kind="icon"]:hover,'
        '[data-testid="stForm"] button[aria-label="Toggle password visibility"]:hover{'
        '    color:#173A7A !important;'
        '    background:transparent !important;'
        '    transform:none !important;'
        '}'
        
        '[data-testid="stForm"] label{'
        '    font-size:12px !important;'
        '    font-weight:600 !important;'
        '    color:#475569 !important;'
        '}'
        
        '[data-testid="stForm"] button[type="submit"],'
        '[data-testid="stFormSubmitButton"] button{'
        '    width:100% !important;'
        '    height:42px !important;'
        '    background:linear-gradient(90deg,#173A7A 0%,#1d52a8 60%,#D8A03F 100%) !important;'
        '    color:white !important;'
        '    border:none !important;'
        '    border-radius:8px !important;'
        '    font-weight:700 !important;'
        '    font-size:14px !important;'
        '    letter-spacing:.3px !important;'
        '    margin-top:12px !important;'
        '    cursor:pointer !important;'
        '    box-shadow:0 2px 8px rgba(23,58,122,.25) !important;'
        '    transition:opacity .15s,transform .1s !important;'
        '}'
        '[data-testid="stFormSubmitButton"] button:hover{'
        '    opacity:.91 !important;'
        '    transform:translateY(-1px) !important;'
        '    box-shadow:0 4px 14px rgba(23,58,122,.30) !important;'
        '}'
        '[data-testid="stFormSubmitButton"] button:active{'
        '    transform:scale(.98) !important;'
        '}'
        '</style>',
        unsafe_allow_html=True
    )

    col_vide, col_form = st.columns([0.60, 0.40])

    with col_form:

        st.markdown(
            '<div class="lc-card">'
            '<div class="lc-bar"></div>'
            '<div class="lc-body">'
            '<div class="lc-logo-row">'
            '<div class="lc-logo-mark">'
            '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M12 2L2 7l10 5 10-5-10-5z"/>'
            '<path d="M2 17l10 5 10-5"/>'
            '<path d="M2 12l10 5 10-5"/>'
            '</svg>'
            '</div>'
            '<div>'
            '<p class="lc-name">ACREMAC</p>'
            '<p class="lc-sub">Scoring IA &middot; Solvabilit&eacute;</p>'
            '</div>'
            '</div>'
            '<div class="lc-divider"></div>'
            '<p class="lc-h2">Connexion</p>'
            '<p class="lc-desc">Moteur IA de scoring de solvabilit&eacute;</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        with st.form("login_form", clear_on_submit=False):
            nom_utilisateur = st.text_input(
                "Identifiant",
                placeholder="Entrez votre identifiant"
            )
            mot_de_passe = st.text_input(
                "Mot de passe",
                type="password",
                placeholder="Entrez votre mot de passe"
            )
            submitted = st.form_submit_button("🔐  Se connecter")

            if submitted:
                if not nom_utilisateur or not mot_de_passe:
                    st.error("❌ Veuillez remplir tous les champs")
                elif nom_utilisateur in UTILISATEURS:
                    mot_de_passe_hache = hashlib.sha256(mot_de_passe.encode()).hexdigest()
                    if mot_de_passe_hache == UTILISATEURS[nom_utilisateur]["mot_de_passe_hache"]:
                        st.session_state["authentifie"]     = True
                        st.session_state["utilisateur"]     = nom_utilisateur
                        st.session_state["nom_utilisateur"] = UTILISATEURS[nom_utilisateur]["nom"]
                        st.session_state["role"]            = UTILISATEURS[nom_utilisateur]["role"]
                        st.rerun()
                    else:
                        st.error("❌ Mot de passe incorrect")
                else:
                    st.error("❌ Nom d'utilisateur inconnu")

        st.markdown(
            '<div class="lc-footer">'
            '<span>🔐 Accès sécurisé</span>'
            '<span class="lc-dot"></span>'
            '<span>Données chiffrées</span>'
            '<span class="lc-dot"></span>'
            '<span>SHA-256</span>'
            '</div>',
            unsafe_allow_html=True
        )

    return False


def deconnecter():
    for key in ["authentifie", "utilisateur", "nom_utilisateur", "role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def get_utilisateur_courant():
    if st.session_state.get("authentifie", False):
        return {
            "login": st.session_state.get("utilisateur", ""),
            "nom":   st.session_state.get("nom_utilisateur", ""),
            "role":  st.session_state.get("role", "")
        }
    return None





















# ============================================================
# 2. COUCHE DONNÉES (SQLite)
# ============================================================

def get_db_connection():
    base = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base, '..', 'database', 'acremac.db')
    return sqlite3.connect(db_path)

def charger_clients_depuis_db():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM clients", conn)
    conn.close()
    return df

def filtrer_clients(pays=None, secteur=None, score_min=None, score_max=None):
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

def get_stats_pays():
    conn = get_db_connection()
    query = """
        SELECT country, COUNT(*) as nb_clients, AVG(solvency_score) as score_moyen
        FROM clients GROUP BY country ORDER BY score_moyen DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_stats_secteur():
    conn = get_db_connection()
    query = """
        SELECT sector, COUNT(*) as nb_clients, AVG(solvency_score) as score_moyen
        FROM clients GROUP BY sector ORDER BY score_moyen DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_stats_categorie():
    conn = get_db_connection()
    query = """
        SELECT 
            CASE 
                WHEN solvency_score >= 680 THEN 'Excellent'
                WHEN solvency_score >= 620 THEN 'Bon'
                WHEN solvency_score >= 560 THEN 'Moyen'
                ELSE 'Risqué'
            END as categorie,
            COUNT(*) as nb_clients
        FROM clients
        GROUP BY categorie
        ORDER BY nb_clients DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# ============================================================
# 3. COUCHE TRAITEMENT
# ============================================================

@st.cache_resource
def charger_modele():
    
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, '..', 'models', 'model_gradient_boosting.pkl'), 'rb') as f:

        model = pickle.load(f)
    return model

@st.cache_resource
def charger_shap():
    
    
    base = os.path.dirname(os.path.abspath(__file__))
    shap_df = pd.read_csv(os.path.join(base, '..', 'shap_results', 'shap_values_df.csv'))
    with open(os.path.join(base, '..', 'shap_results', 'shap_config.json'), 'r') as f:
        config = json.load(f)
    return shap_df, config

def preprocesser_pour_modele(df_brut):
    """Prétraitement des données (identique à Phase 2)"""
    df = df_brut.copy()

    if 'client_id' in df.columns:
        df = df.drop(columns=['client_id'])

    df['client_type'] = (df['client_type'] == 'Personne_physique').astype(int)

    df = pd.get_dummies(
        df,
        columns=['sector', 'country'],
        drop_first=True
    )

    X = df.drop(columns=['solvency_score'], errors='ignore')

    return X
def preprocesser_et_aligner(df_brut, colonnes_reference):
    X = preprocesser_pour_modele(df_brut)
    return X.reindex(columns=colonnes_reference, fill_value=0)
def predire_score(model, X, idx):
    return float(model.predict(X.iloc[[idx]])[0])


# ============================================================
# 3.1 SYSTÈME DE RÉENTRAÎNEMENT AUTOMATIQUE
# ============================================================

import schedule
import time
import threading

def reentrainer_modele_en_background():
    """Fonction de réentraînement automatique (à exécuter en tâche de fond)"""
    try:
        df_brut = charger_clients_depuis_db()
        df = df_brut.copy()
        df = df.drop(columns=['client_id'])
        df['client_type'] = (df['client_type'] == 'Personne_physique').astype(int)
        df = pd.get_dummies(df, columns=['sector', 'country'], drop_first=True)
        X = df.drop(columns=['solvency_score'])
        y = df['solvency_score']
        
        from sklearn.ensemble import GradientBoostingRegressor
        nouveau_modele = GradientBoostingRegressor(
            n_estimators=200, learning_rate=0.05, max_depth=4, random_state=42
        )
        nouveau_modele.fit(X, y)
        
        base = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base, '..', 'models', 'model_gradient_boosting_v2.pkl'), 'wb') as f:
            pickle.dump(nouveau_modele, f)
        
        # Mise à jour du cache Streamlit
        st.cache_resource.clear()
        return True
    except Exception as e:
        print(f"❌ Erreur réentraînement : {e}")
        return False

def planifier_reentrainement():
    """Planifie le réentraînement chaque semaine (dimanche à 3h)"""
    schedule.every().sunday.at("03:00").do(reentrainer_modele_en_background)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    return thread

# Démarrer le planificateur au lancement (optionnel)
# planifier_reentrainement()






# ============================================================
# 4. COUCHE EXPLICABILITÉ (SHAP)
# ============================================================

def categorie_du_score(score):
    if score >= 680:
        return "Excellent", "#10b981", "💳 Crédit recommandé"
    elif score >= 620:
        return "Bon", "#f59e0b", "✅ Conditions standard"
    elif score >= 560:
        return "Moyen", "#f97316", "⚠️ Garanties renforcées"
    else:
        return "Risqué", "#ef4444", "🚫 Crédit refusé"

def afficher_waterfall(idx, model, X, shap_df, base_value):
    shap_client = shap_df.iloc[idx]
    top_10 = shap_client.abs().sort_values(ascending=False).head(10)
    shap_sorted = shap_client[top_10.index].sort_values()
    score = predire_score(model, X, idx)
    categorie, couleur, _ = categorie_du_score(score)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#ef4444' if v < 0 else '#10b981' for v in shap_sorted.values]
    bars = ax.barh(range(len(shap_sorted)), shap_sorted.values, color=colors, height=0.6)
    ax.set_yticks(range(len(shap_sorted)))
    ax.set_yticklabels(shap_sorted.index, fontsize=10)
    ax.axvline(0, color='black', linewidth=1)
    for bar, val in zip(bars, shap_sorted.values):
        ax.text(val + (0.3 if val >= 0 else -0.3), 
                bar.get_y() + bar.get_height()/2,
                f'{val:+.1f}', va='center',
                ha='left' if val >= 0 else 'right', fontsize=9, fontweight='bold')
    ax.set_title(f'Score: {score:.0f} pts · {categorie} · Référence: {base_value:.0f} pts', fontsize=12)
    ax.set_xlabel('Contribution (points)')
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color='#10b981', label='Augmente le score'),
                       Patch(color='#ef4444', label='Diminue le score')], loc='lower right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()




# ============================================================
# 4.1 SUIVI DES PERFORMANCES (MONITORING)
# ============================================================

import pandas as pd
import os

def get_historique_performances():
    """Charge l'historique des performances depuis un fichier CSV"""
    base = os.path.dirname(os.path.abspath(__file__))
    hist_path = os.path.join(base, '..', 'models', 'historique_performances.csv')
    
    if os.path.exists(hist_path):
        df_hist = pd.read_csv(hist_path)
        return df_hist
    else:
        # Créer un historique initial
        df_hist = pd.DataFrame({
            'date': [pd.Timestamp.now().strftime('%Y-%m-%d')],
            'r2': [0.9449],
            'rmse': [13.51],
            'mae': [9.76]
        })
        df_hist.to_csv(hist_path, index=False)
        return df_hist

def ajouter_performance(date, r2, rmse, mae):
    """Ajoute une nouvelle performance à l'historique"""
    base = os.path.dirname(os.path.abspath(__file__))
    hist_path = os.path.join(base, '..', 'models', 'historique_performances.csv')
    
    df_hist = get_historique_performances()
    nouvelle_ligne = pd.DataFrame({
        'date': [date],
        'r2': [r2],
        'rmse': [rmse],
        'mae': [mae]
    })
    df_hist = pd.concat([df_hist, nouvelle_ligne], ignore_index=True)
    df_hist.to_csv(hist_path, index=False)
    return df_hist

# Dans la page Tableau de bord, ajouter un onglet "📈 Monitoring"
# Voir la section d'ajout dans les pages




# ============================================================
# 4.2 NOTIFICATIONS & ALERTES AUTOMATIQUES
# ============================================================

def envoyer_alerte(client_id, score, categorie, facteur_principal):
    """Envoie une alerte par email (simulation)"""
    # Simulation d'envoi d'email
    print(f"""
    ⚠️ ALERTE CLIENT RISQUÉ
    Client : {client_id}
    Score : {score:.0f}/737
    Catégorie : {categorie}
    Facteur principal : {facteur_principal}
    """)
    
    # En production, utiliser smtplib :
    # import smtplib
    # from email.mime.text import MIMEText
    # ...

def verifier_clients_risques():
    """Vérifie les clients à risque et déclenche des alertes"""
    for idx, row in df_brut.iterrows():
        score = predire_score(model, X, idx)
        categorie, _, _ = categorie_du_score(score)
        
        if categorie == "Risqué":
            client_id = row['client_id']
            shap_client = shap_df.iloc[idx]
            facteur_principal = shap_client.sort_values(ascending=True).head(1).index[0]
            
            # Stocker dans un fichier d'alertes
            base = os.path.dirname(os.path.abspath(__file__))
            alert_path = os.path.join(base, '..', 'logs', 'alertes.csv')
            os.makedirs(os.path.dirname(alert_path), exist_ok=True)
            
            try:
                df_alert = pd.read_csv(alert_path)
            except:
                df_alert = pd.DataFrame(columns=['date', 'client_id', 'score', 'categorie', 'facteur'])
            
            nouvelle_alerte = pd.DataFrame([{
                'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                'client_id': client_id,
                'score': round(score, 0),
                'categorie': categorie,
                'facteur': facteur_principal
            }])
            df_alert = pd.concat([df_alert, nouvelle_alerte], ignore_index=True)
            df_alert.to_csv(alert_path, index=False)
            
            envoyer_alerte(client_id, score, categorie, facteur_principal)

# Lancer la vérification au chargement (optionnel)
# verifier_clients_risques()

# Dans la page Tableau de bord, ajouter un affichage des alertes




# ============================================================
# 5. CHARGEMENT GLOBAL
# ============================================================

@st.cache_resource
def charger_toutes_donnees():

    df_brut = charger_clients_depuis_db()

    model = charger_modele()

    X = preprocesser_pour_modele(df_brut)

    y_pred = model.predict(X)

    # ─────────────────────────────────────────────
    # Calcul dynamique des valeurs SHAP
    # ─────────────────────────────────────────────
    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X)

    shap_df = pd.DataFrame(
        shap_values,
        columns=X.columns,
        index=X.index
    )

    base_value = float(np.ravel(explainer.expected_value)[0])

    config = {
        "base_value": base_value
    }

    return (
        df_brut,
        model,
        shap_df,
        config,
        X,
        y_pred,
        base_value
    )



# ============================================================
# 6. CONFIGURATION STREAMLIT & INFRASTRUCTURE GRAPHICS
# ============================================================

st.set_page_config(page_title="ACREMAC Scoring", page_icon="🏦", layout="wide")

# ─── AUTHENTIFICATION ──────────────────────────────────────────────────────────
if not verifier_authentification():
    st.stop()

# ─── TRAITEMENT DE L'IMAGE D'ARRIÈRE-PLAN DE LA SIDEBAR ───────────────────────
path_bg_sidebar = os.path.join(
    BASE_DIR,
    "images",
    "side_arriere.jpg"
)
bg_sidebar_css = ""

if os.path.exists(path_bg_sidebar):
    try:
        import base64
        with open(path_bg_sidebar, "rb") as f:
            encoded_bg = base64.b64encode(f.read()).decode()
        bg_sidebar_css = f"background-image: url('data:image/jpeg;base64,{encoded_bg}') !important; background-size: cover !important; background-position: center !important;"
    except Exception:
        bg_sidebar_css = "background: #f8fafc !important;"
else:
    bg_sidebar_css = "background: #f8fafc !important;"

# ─── STYLE CSS GENERAL EDITIONS GRAPHES MODERNE (REPLICA IMAGE) ───────────────
# Tout le style CSS est condensé sur une seule ligne pour éliminer le bug d'affichage brut
st.markdown(f"<style>.stApp {{ background: #f8fafc; }} .main-header {{ background: linear-gradient(135deg, #0b1a30 0%, #16325c 60%, #1d4b88 100%); padding: 28px 32px; border-radius: 16px; color: white; margin-bottom: 24px; position: relative; }} [data-testid='stSidebar'] {{ {bg_sidebar_css} border-right: 1px solid #e2e8f0 !important; min-width: 280px !important; max-width: 280px !important; padding: 20px 10px !important; }} [data-testid='stSidebar'] * {{ color: #4a5568 !important; }} .sb-glass-container {{ background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.6); padding: 24px 18px; box-shadow: 0 10px 30px rgba(0,0,0,0.04); display: flex; flex-direction: column; gap: 8px; }} .sb-user-card {{ display: flex; align-items: center; gap: 14px; padding-bottom: 18px; border-bottom: 1px solid rgba(0,0,0,0.06); margin-bottom: 12px; }} .sb-avatar {{ width: 44px; height: 44px; background: #e2e8f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; }} .sb-u-info {{ display: flex; flex-direction: column; }} .sb-u-name {{ font-size: 1.05rem; font-weight: 700; color: #1a202c !important; }} .sb-u-sub {{ font-size: 0.8rem; color: #718096 !important; }} .sb-menu-title {{ font-size: 1.1rem; font-weight: 700; color: #2d3748 !important; margin: 8px 0 4px 6px; }} [data-testid='stSidebar'] .stRadio > div {{ display: flex; flex-direction: column; gap: 2px; padding: 0 !important; }} [data-testid='stSidebar'] .stRadio label {{ display: flex !important; align-items: center !important; padding: 10px 12px !important; border-radius: 12px !important; cursor: pointer !important; transition: all 0.2s ease !important; font-weight: 500 !important; font-size: 0.95rem !important; color: #4a5568 !important; background: transparent !important; border: none !important; margin: 0 !important; width: 100% !important; }} [data-testid='stSidebar'] .stRadio label:hover {{ background-color: rgba(0, 0, 0, 0.04) !important; color: #1a202c !important; }} [data-testid='stSidebar'] .stRadio input:checked + div {{ background-color: transparent !important; border-radius: 0px !important; }} [data-testid='stSidebar'] .stRadio input:checked + div * {{ color: #2b6cb0 !important; font-weight: 700 !important; }} .sb-logout-box {{ border-top: 1px solid rgba(0,0,0,0.06); margin-top: 12px; padding-top: 14px; }} [data-testid='stSidebar'] .stButton > button {{ background: transparent !important; color: #4a5568 !important; border: none !important; border-radius: 12px !important; font-weight: 500 !important; font-size: 0.95rem !important; padding: 10px 12px !important; width: 100% !important; transition: all 0.2s; display: flex; align-items: center; justify-content: flex-start !important; gap: 10px; text-align: left !important; box-shadow: none !important; }} [data-testid='stSidebar'] .stButton > button:hover {{ background: rgba(0,0,0,0.04) !important; color: #1a202c !important; }} [data-testid='stSelectbox'] div[data-testid='stWidgetLabel'] label {{ background: #ffffff !important; color: #2d3748 !important; font-weight: 600 !important; font-size: 0.85rem !important; padding: 5px 12px !important; border-radius: 20px !important; border: 1px solid #cbd5e1 !important; display: inline-flex !important; align-items: center !important; gap: 6px !important; margin-bottom: 6px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important; }} #MainMenu, footer, header {{ visibility: hidden; }}</style>", unsafe_allow_html=True)

# ─── CHARGEMENT DES DONNÉES ──────────────────────────────────────────────────
try:
    df_brut, model, shap_df, config, X, y_pred, base_value = charger_toutes_donnees()
    CHARGEMENT_OK = True
except Exception as e:
    CHARGEMENT_OK = False
    ERREUR = str(e)

if not CHARGEMENT_OK:
    st.error(f"Erreur de chargement : {ERREUR}")
    st.stop()

# ─── CONSTRUCION DE LA SIDEBAR TRANSLUCIDE (GLASSMORPHISM) ────────────────────
with st.sidebar:
    
    # Ouverture du conteneur en verre arrondi
    st.markdown("<div class='sb-glass-container'>", unsafe_allow_html=True)
    
    # 1. Profil Utilisateur haut de page (Inspiré de la structure demandée)
    util_nom = st.session_state.get('nom_utilisateur', 'Username')
    st.markdown(f"""
    <div class='sb-user-card'>
        <div class='sb-avatar'>👤</div>
        <div class='sb-u-info'>
            <span class='sb-u-name'>{util_nom}</span>
            <span class='sb-u-sub'>Mon Compte</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Titre de la section Menu
    st.markdown("<div class='sb-menu-title'>Menu</div>", unsafe_allow_html=True)
    
    # 2. Navigation Radio Streamlit (Intercepte dynamiquement les clics sans boutons HTML bruts)
    page = st.radio(
        "Navigation",
        ["🏠 Accueil", "📊 Tableau de bord", "👥 Gestion des clients", "👤 Analyse client", "📄 Rapport"],
        label_visibility="collapsed"
    )
    
    
    # 3. Bouton Déconnexion épuré intégré en bas du conteneur transparent
    st.markdown("<div class='sb-logout-box'></div>", unsafe_allow_html=True)
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state["authentifie"] = False
        st.session_state["utilisateur"] = None
        st.rerun()
        
    # Fermeture du conteneur
    st.markdown("</div>", unsafe_allow_html=True)
















# ============================================================
# PAGE : ACCUEIL — VERSION WAOUH AVEC ANIMATIONS
# ============================================================

if page == "🏠 Accueil":
    
    import base64
    
    # ─── CHARGEMENT DES IMAGES EN BASE64 ──────────────────────────────────
    def get_image_base64(image_path):
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_dir = os.path.join(BASE_DIR, "images")
    img_banniere_b64 = get_image_base64(os.path.join(base_dir, "arriere_banniere.png"))
    img_accueil_b64  = get_image_base64(os.path.join(base_dir, "arriere_accueil.png"))

    # ─── CSS GLOBAL PAGE + ANIMATIONS ─────────────────────────────────────
    # L'image de fond page est injectée via un sélecteur très spécifique
    page_bg_css = ""
    if img_accueil_b64:
        page_bg_css = f"""
        .stApp {{
            background-image: url('data:image/png;base64,{img_accueil_b64}') !important;
            background-size: cover !important;
            background-position: center top !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        """

    banner_bg = ""
    if img_banniere_b64:
        banner_bg = f"""
            background-image: url('data:image/png;base64,{img_banniere_b64}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        """
    else:
        banner_bg = "background: linear-gradient(135deg, #0b1a30 0%, #16325c 40%, #1d4b88 100%);"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
        
        * {{ font-family: 'Inter', sans-serif; }}

        {page_bg_css}

        /* ── Animations ── */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(40px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes countUp {{
            from {{ opacity: 0; transform: translateY(30px) scale(0.8); }}
            to {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}
        @keyframes shimmer {{
            0% {{ background-position: -200% center; }}
            100% {{ background-position: 200% center; }}
        }}
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-8px); }}
        }}
        @keyframes rotateGlow {{
            0% {{ transform: rotate(0deg); opacity: 0.3; }}
            50% {{ opacity: 0.8; }}
            100% {{ transform: rotate(360deg); opacity: 0.3; }}
        }}

        .animate-fade {{ animation: fadeInUp 0.7s ease-out; }}
        .animate-count {{ animation: countUp 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards; }}
        .animate-float {{ animation: float 3s ease-in-out infinite; }}

        /* ── Banner Premium ── */
        .premium-banner {{
            {banner_bg}
            padding: 45px 50px;
            border-radius: 24px;
            color: white;
            margin-bottom: 35px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(11,26,48,0.40);
            animation: fadeInUp 0.6s ease-out;
        }}
        .premium-banner::before {{
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(11,26,48,0.72) 0%, rgba(22,50,92,0.60) 50%, rgba(29,75,136,0.50) 100%);
            border-radius: 24px;
            z-index: 0;
        }}
        .premium-banner > * {{
            position: relative;
            z-index: 1;
        }}
        .banner-tagline {{
            color: #ffd166;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 6px;
        }}
        .banner-main-title {{
            font-size: 2.6rem;
            font-weight: 900;
            margin: 0 0 8px 0;
            color: #ffffff;
            letter-spacing: -1px;
            text-shadow: 0 2px 12px rgba(0,0,0,0.35);
        }}
        .banner-description {{
            color: rgba(255,255,230,0.88);
            font-size: 1.05rem;
            margin: 0 0 20px 0;
            font-weight: 400;
        }}
        .banner-meta {{
            display: flex;
            gap: 24px;
            font-size: 0.8rem;
            color: rgba(255,240,180,0.80);
            align-items: center;
            flex-wrap: wrap;
        }}
        .meta-item {{ display: flex; align-items: center; gap: 8px; }}
        .meta-dot {{ width: 4px; height: 4px; background: rgba(255,220,100,0.40); border-radius: 50%; }}

        /* ── KPI Cards ── */
        .kpi-premium-card {{
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 24px 28px;
            border: 1px solid rgba(255,255,255,0.5);
            box-shadow: 0 8px 32px rgba(0,0,0,0.10);
            display: flex;
            align-items: center;
            gap: 20px;
            height: 100%;
            transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
            cursor: default;
            position: relative;
            overflow: hidden;
        }}
        .kpi-premium-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(90deg, #0d1f3c, #1a5fa0, #D8A03F);
            background-size: 200% 100%;
            animation: shimmer 3s infinite;
        }}
        .kpi-premium-card:hover {{
            transform: translateY(-6px) scale(1.01);
            box-shadow: 0 20px 50px rgba(0,0,0,0.16);
        }}
        .kpi-icon-wrapper-premium {{
            width: 56px; height: 56px;
            border-radius: 16px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.6rem; flex-shrink: 0;
            transition: transform 0.3s;
        }}
        .kpi-premium-card:hover .kpi-icon-wrapper-premium {{
            transform: scale(1.1) rotate(5deg);
        }}
        .kpi-details-premium {{ display: flex; flex-direction: column; }}
        .kpi-title-premium {{
            font-size: 0.7rem; color: #64748b; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 2px;
        }}
        .kpi-value-premium {{
            font-size: 2.2rem; font-weight: 900; line-height: 1.1; color: #0d1f3c;
        }}
        .kpi-sub-premium {{ font-size: 0.75rem; color: #94a3b8; margin-top: 2px; }}
        .kpi-trend {{
            font-size: 0.7rem; font-weight: 700;
            padding: 2px 12px; border-radius: 50px;
            display: inline-block; margin-top: 2px;
        }}

        /* ── Risk Cards ── */
        .risk-premium-card {{
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.5);
            padding: 30px 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            text-align: center;
            height: 100%;
            transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
            position: relative; overflow: hidden; cursor: default;
        }}
        .risk-premium-card:hover {{
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 20px 50px rgba(0,0,0,0.12);
        }}
        .risk-premium-card .risk-bar {{
            position: absolute; bottom: 0; left: 0;
            height: 5px; transition: all 0.6s;
        }}
        .risk-premium-card:hover .risk-bar {{ height: 7px; }}
        .risk-icon-premium {{
            width: 70px; height: 70px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 2rem; margin: 0 auto 14px auto;
            transition: transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
        }}
        .risk-premium-card:hover .risk-icon-premium {{
            transform: scale(1.1) rotate(10deg);
        }}
        .risk-number-premium {{
            font-size: 2.4rem; font-weight: 900;
            line-height: 1; margin-bottom: 4px; color: #0d1f3c;
        }}
        .risk-label-premium {{
            font-weight: 700; color: #64748b;
            font-size: 0.95rem; margin-bottom: 12px;
        }}
        .risk-badge-premium {{
            display: inline-block; padding: 6px 18px;
            border-radius: 50px; font-size: 0.75rem;
            font-weight: 700; transition: transform 0.3s;
        }}
        .risk-premium-card:hover .risk-badge-premium {{ transform: scale(1.05); }}

        /* ── Section Titles ── */
        .section-premium-title {{
            font-size: 1.1rem; font-weight: 800; color: #0d1f3c;
            text-transform: uppercase; letter-spacing: 1px;
            margin-top: 40px; margin-bottom: 20px;
            display: flex; align-items: center; gap: 12px;
            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            padding: 10px 18px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.4);
        }}
        .section-premium-title::after {{
            content: ''; flex: 1; height: 2px;
            background: linear-gradient(90deg, #e2e8f0, transparent);
        }}

        /* ── Academic Box ── */
        .academic-premium-box {{
            background: rgba(255,255,255,0.93);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 24px;
            border: 1px solid rgba(255,255,255,0.5);
            padding: 32px; margin-top: 35px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            transition: all 0.4s;
        }}
        .academic-premium-box:hover {{
            box-shadow: 0 20px 50px rgba(0,0,0,0.10);
        }}
        .tech-block-premium {{
            border-radius: 14px; padding: 20px 24px;
            display: flex; gap: 16px; align-items: flex-start;
            transition: all 0.3s; border: 1px solid transparent;
        }}
        .tech-block-premium:hover {{
            transform: translateY(-3px); border-color: rgba(0,0,0,0.04);
        }}
        .tech-icon-premium {{ font-size: 2rem; flex-shrink: 0; margin-top: 2px; }}
        .tech-content-premium h4 {{
            margin: 0 0 4px 0; font-size: 0.85rem;
            font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;
        }}
        .tech-content-premium p {{
            margin: 0; font-size: 0.85rem; color: #475569; line-height: 1.6;
        }}

        /* ── Alertes ── */
        .alert-premium {{
            background: rgba(254,242,242,0.92);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid #fecaca;
            border-radius: 14px; padding: 14px 20px;
            margin: 8px 0; display: flex;
            align-items: center; gap: 14px; transition: all 0.3s;
        }}
        .alert-premium:hover {{
            transform: translateX(6px);
            box-shadow: 0 4px 16px rgba(239,68,68,0.12);
        }}

        /* ── Responsive ── */
        @media (max-width: 768px) {{
            .banner-main-title {{ font-size: 1.6rem; }}
            .premium-banner {{ padding: 28px 24px; }}
            .kpi-premium-card {{ padding: 18px 16px; }}
            .kpi-value-premium {{ font-size: 1.6rem; }}
        }}
    </style>
    """, unsafe_allow_html=True)

    # ─── BANNER ANIMÉ ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="premium-banner">
        <div class="banner-tagline">🚀 Plateforme IA d'évaluation du risque de crédit</div>
        <h1 class="banner-main-title">Moteur Décisionnel de Scoring de Solvabilité</h1>
        <p class="banner-description">Solution d'intelligence artificielle pour une gestion avancée du risque de crédit</p>
        <div class="banner-meta">
            <div class="meta-item">🏢 <strong>ACREMAC Africa</strong></div>
            <span class="meta-dot"></span>
            <div class="meta-item">🛡️ Excellence</div>
            <span class="meta-dot"></span>
            <div class="meta-item">🔍 Transparence</div>
            <span class="meta-dot"></span>
            <div class="meta-item">💡 Innovation</div>
            <span class="meta-dot"></span>
            <div class="meta-item">⚡ Temps réel</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not CHARGEMENT_OK:
        st.error(f"❌ Erreur de chargement : {ERREUR}")
        st.stop()

    # ─── KPIS ──────────────────────────────────────────────────────────────
    total_clients = len(df_brut)
    score_moyen   = y_pred.mean() if len(y_pred) > 0 else 0
    score_min     = y_pred.min()  if len(y_pred) > 0 else 0
    score_max     = y_pred.max()  if len(y_pred) > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-premium-card animate-count">
            <div class="kpi-icon-wrapper-premium" style="background:rgba(13,31,60,0.06);color:#0d1f3c;">👥</div>
            <div class="kpi-details-premium">
                <div class="kpi-title-premium">Portefeuille Clients</div>
                <div class="kpi-value-premium">{total_clients:,}</div>
                <div class="kpi-sub-premium">Clients analysés</div>
                <span class="kpi-trend" style="background:#ecfdf5;color:#10b981;">📈 +0%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-premium-card animate-count" style="animation-delay:0.1s;">
            <div class="kpi-icon-wrapper-premium" style="background:rgba(16,185,129,0.08);color:#10b981;">📈</div>
            <div class="kpi-details-premium">
                <div class="kpi-title-premium">Score Moyen</div>
                <div class="kpi-value-premium" style="color:#10b981;">{score_moyen:.0f}<span style="font-size:1rem;font-weight:600;"> pts</span></div>
                <div class="kpi-sub-premium">Score prédictif moyen</div>
                <span class="kpi-trend" style="background:#ecfdf5;color:#10b981;">✅ Stable</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-premium-card animate-count" style="animation-delay:0.2s;">
            <div class="kpi-icon-wrapper-premium" style="background:rgba(245,158,11,0.08);color:#f59e0b;">📉</div>
            <div class="kpi-details-premium">
                <div class="kpi-title-premium">Score Minimum</div>
                <div class="kpi-value-premium" style="color:#f59e0b;">{score_min:.0f}</div>
                <div class="kpi-sub-premium">Client le plus risqué</div>
                <span class="kpi-trend" style="background:#fef2f2;color:#ef4444;">⚠️ À surveiller</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-premium-card animate-count" style="animation-delay:0.3s;">
            <div class="kpi-icon-wrapper-premium" style="background:rgba(30,75,138,0.08);color:#1d4b88;">📊</div>
            <div class="kpi-details-premium">
                <div class="kpi-title-premium">Score Maximum</div>
                <div class="kpi-value-premium" style="color:#1d4b88;">{score_max:.0f}</div>
                <div class="kpi-sub-premium">Client le plus solvable</div>
                <span class="kpi-trend" style="background:#ecfdf5;color:#10b981;">🏆 Excellent</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── MÉTRIQUES AVANCÉES ────────────────────────────────────────────────
    st.markdown("""
    <div class="section-premium-title">📊 Métriques avancées du portefeuille</div>
    """, unsafe_allow_html=True)

    nb_excellent = sum(1 for s in y_pred if s >= 680)
    nb_bon       = sum(1 for s in y_pred if 620 <= s < 680)
    nb_moyen     = sum(1 for s in y_pred if 560 <= s < 620)
    nb_risque    = sum(1 for s in y_pred if s < 560)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("🟢 Excellent", nb_excellent, delta=f"{nb_excellent/total_clients*100:.1f}%", delta_color="normal")
    with col_m2:
        st.metric("🟡 Bon", nb_bon, delta=f"{nb_bon/total_clients*100:.1f}%", delta_color="normal")
    with col_m3:
        st.metric("🟠 Moyen", nb_moyen, delta=f"{nb_moyen/total_clients*100:.1f}%", delta_color="normal")
    with col_m4:
        st.metric("🔴 Risqué", nb_risque, delta=f"{nb_risque/total_clients*100:.1f}%", delta_color="inverse")

    # ─── RÉPARTITION DES RISQUES ───────────────────────────────────────────
    st.markdown("""
    <div class="section-premium-title">📊 Répartition des profils de risques</div>
    """, unsafe_allow_html=True)

    cats   = [categorie_du_score(s)[0] for s in y_pred]
    counts = Counter(cats)

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        n   = counts.get("Excellent", 0)
        pct = (n / total_clients * 100) if total_clients > 0 else 0
        st.markdown(f"""
        <div class="risk-premium-card animate-count">
            <div class="risk-icon-premium" style="background:rgba(16,185,129,0.08);color:#10b981;">🛡️</div>
            <div class="risk-number-premium">{n}</div>
            <div class="risk-label-premium">Excellent</div>
            <div class="risk-badge-premium" style="background:rgba(16,185,129,0.10);color:#10b981;">{pct:.1f}%</div>
            <div class="risk-bar" style="background:#10b981;width:{pct}%;"></div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        n   = counts.get("Bon", 0)
        pct = (n / total_clients * 100) if total_clients > 0 else 0
        st.markdown(f"""
        <div class="risk-premium-card animate-count" style="animation-delay:0.1s;">
            <div class="risk-icon-premium" style="background:rgba(245,158,11,0.08);color:#f59e0b;">⭐</div>
            <div class="risk-number-premium">{n}</div>
            <div class="risk-label-premium">Bon</div>
            <div class="risk-badge-premium" style="background:rgba(245,158,11,0.10);color:#f59e0b;">{pct:.1f}%</div>
            <div class="risk-bar" style="background:#f59e0b;width:{pct}%;"></div>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        n   = counts.get("Moyen", 0)
        pct = (n / total_clients * 100) if total_clients > 0 else 0
        st.markdown(f"""
        <div class="risk-premium-card animate-count" style="animation-delay:0.2s;">
            <div class="risk-icon-premium" style="background:rgba(249,115,22,0.08);color:#f97316;">➖</div>
            <div class="risk-number-premium">{n}</div>
            <div class="risk-label-premium">Moyen</div>
            <div class="risk-badge-premium" style="background:rgba(249,115,22,0.10);color:#f97316;">{pct:.1f}%</div>
            <div class="risk-bar" style="background:#f97316;width:{pct}%;"></div>
        </div>
        """, unsafe_allow_html=True)

    with col_d:
        n   = counts.get("Risqué", 0)
        pct = (n / total_clients * 100) if total_clients > 0 else 0
        st.markdown(f"""
        <div class="risk-premium-card animate-count" style="animation-delay:0.3s;">
            <div class="risk-icon-premium" style="background:rgba(239,68,68,0.08);color:#ef4444;">⚠️</div>
            <div class="risk-number-premium">{n}</div>
            <div class="risk-label-premium">Risqué</div>
            <div class="risk-badge-premium" style="background:rgba(239,68,68,0.10);color:#ef4444;">{pct:.1f}%</div>
            <div class="risk-bar" style="background:#ef4444;width:{pct}%;"></div>
        </div>
        """, unsafe_allow_html=True)

    # ─── TABLEAU TOP / BOTTOM ──────────────────────────────────────────────
    st.markdown("""
    <div class="section-premium-title">🏆 Clients les plus solvables & ⚠️ Clients à risque</div>
    """, unsafe_allow_html=True)

    col_top, col_bottom = st.columns(2)

    with col_top:
        st.markdown("#### 🏆 Meilleurs scores")
        top_clients = df_brut.nlargest(5, 'solvency_score')[['client_id', 'solvency_score', 'country', 'sector']]
        top_clients.columns = ['Client ID', 'Score', 'Pays', 'Secteur']
        st.dataframe(top_clients, use_container_width=True, hide_index=True)

    with col_bottom:
        st.markdown("#### ⚠️ Scores les plus faibles")
        bottom_clients = df_brut.nsmallest(5, 'solvency_score')[['client_id', 'solvency_score', 'country', 'sector']]
        bottom_clients.columns = ['Client ID', 'Score', 'Pays', 'Secteur']
        st.dataframe(bottom_clients, use_container_width=True, hide_index=True)

    # ─── ALERTES ──────────────────────────────────────────────────────────
    base_path  = os.path.dirname(os.path.abspath(__file__))
    alert_path = os.path.join(base_path, '..', 'logs', 'alertes.csv')

    if os.path.exists(alert_path):
        df_alert = pd.read_csv(alert_path).tail(5)
        st.markdown("""
        <div class="section-premium-title">🚨 Alertes récentes</div>
        """, unsafe_allow_html=True)
        for _, row in df_alert.iterrows():
            st.markdown(f"""
            <div class="alert-premium animate-fade">
                <span style="font-size:1.4em;">🔴</span>
                <div>
                    <strong>{row['client_id']}</strong>
                    <span style="color:#64748b;font-size:0.85em;">· Score : {row['score']:.0f}</span>
                    <span style="color:#64748b;font-size:0.85em;">· Facteur : {row['facteur']}</span>
                </div>
                <span style="margin-left:auto;font-size:0.7em;color:#94a3b8;">{row['date']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Aucune alerte enregistrée")

    # ─── CONTEXTE ACADÉMIQUE ──────────────────────────────────────────────
    st.markdown("""
    <div class="academic-premium-box animate-fade">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <span style="font-size:1.8em;">🎓</span>
            <div>
                <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#94a3b8;">Contexte</div>
                <div style="font-size:1.1rem;font-weight:800;color:#0d1f3c;">Académique & Industriel</div>
            </div>
        </div>
        <div style="color:#475569;font-size:0.95rem;line-height:1.7;margin-bottom:24px;">
            Ce système décisionnel a été intégralement conçu et développé dans le cadre du <strong>Projet de Fin d'Études (PFE)</strong>
            au sein de l'école d'ingénieurs <strong>HESTIM MAROC</strong> pour le compte d'<strong>ACREMAC</strong>
            (Africa Credit Management Insurances & Consulting), institution majeure de centralisation et de gouvernance
            des données de crédit en Afrique Centrale.
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;">
            <div class="tech-block-premium" style="background:#fffcf8;border:1px solid #ffedd5;">
                <div class="tech-icon-premium">🧠</div>
                <div class="tech-content-premium">
                    <h4 style="color:#ea580c;">Pipeline IA</h4>
                    <p><strong>Machine Learning :</strong> Modélisation prédictive par Gradient Boosting optimisé.</p>
                </div>
            </div>
            <div class="tech-block-premium" style="background:#f0fdf4;border:1px solid #dcfce7;">
                <div class="tech-icon-premium">⚖️</div>
                <div class="tech-content-premium">
                    <h4 style="color:#16a34a;">Explicabilité</h4>
                    <p><strong>Théorie des Jeux (SHAP) :</strong> Transparence totale des variables explicatives par dossier.</p>
                </div>
            </div>
            <div class="tech-block-premium" style="background:#f0fdfa;border:1px solid #ccfbf1;">
                <div class="tech-icon-premium">🗄️</div>
                <div class="tech-content-premium">
                    <h4 style="color:#0d9488;">Infrastructure</h4>
                    <p><strong>Architecture 4 Couches :</strong> Données, Traitement, Explicabilité, Présentation.</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)



























# ============================================================
# PAGE : GESTION DES CLIENTS (Ajouter · Supprimer · Modifier)
# ============================================================

elif page == "👥 Gestion des clients":
    st.markdown("""
    <div class="main-header">
        <h1 style="color:white;margin:0;">👥 Gestion des clients</h1>
        <p style="color:rgba(255,255,255,0.8);margin:4px 0 0;">Ajouter, modifier ou supprimer des clients de la base ACREMAC</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Affichage du message de succès après un rerun ──────────────
    if "message_succes" in st.session_state:
        st.success(st.session_state["message_succes"])
        del st.session_state["message_succes"]

    # ─── Onglets ──────────────────────────────────────────────────────────────
    tab_ajouter, tab_consulter, tab_modifier, tab_supprimer = st.tabs([
        "➕ Ajouter un client",
        "📋 Consulter les clients",
        "✏️ Modifier un client",
        "🗑️ Supprimer un client"
    ])
    
    # ─── TAB 1 : AJOUTER UN CLIENT ─────────────────────────────────────────
    with tab_ajouter:
        st.markdown("### 📝 Ajouter un nouveau client")
        
        with st.form("form_ajout_client"):
            st.markdown("#### 📋 Informations générales")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                client_id = st.text_input("ID Client", placeholder="ex: C100200")
                client_type = st.selectbox("Type de client", ["Personne_physique", "Personne_morale"])
                age = st.number_input("Âge", min_value=18, max_value=100, value=35)
            
            with col2:
                pays = st.selectbox("Pays", ["Cameroun", "Congo", "Gabon", "Tchad"])
                secteur = st.selectbox("Secteur", ["Agriculture", "Commerce", "Industrie", "Services", "Transport"])
                annual_income = st.number_input("Revenu annuel", min_value=100000, max_value=50000000, value=15000000, step=100000)
            
            with col3:
                loan_amount = st.number_input("Montant du crédit", min_value=500000, max_value=20000000, value=5000000, step=100000)
                loan_duration = st.selectbox("Durée du crédit (mois)", [12, 24, 36, 48, 60])
                interest_rate = st.number_input("Taux d'intérêt (%)", min_value=1.0, max_value=20.0, value=8.0, step=0.1)
            
            st.markdown("#### 📊 Historique de paiement")
            
            col4, col5, col6 = st.columns(3)
            with col4:
                past_defaults = st.number_input("Défauts passés", min_value=0, max_value=5, value=0)
                credit_history_years = st.number_input("Ancienneté crédit (années)", min_value=0, max_value=30, value=10)
            with col5:
                existing_loans = st.number_input("Crédits en cours", min_value=0, max_value=10, value=0)
                monthly_payment_ratio = st.number_input("Ratio mensualité/revenu", min_value=0.0, max_value=1.0, value=0.3, step=0.01)
            with col6:
                collateral_value = st.number_input("Valeur de la garantie", min_value=0, max_value=50000000, value=5000000, step=100000)
                days_late_avg = st.number_input("Retard moyen (jours)", min_value=0, max_value=120, value=0)
            
            submitted = st.form_submit_button("💾 Ajouter le client", use_container_width=True)
            
            if submitted:
                if not client_id:
                    st.error("❌ L'ID client est obligatoire")
                elif client_id in df_brut['client_id'].values:
                    st.error(f"❌ L'ID {client_id} existe déjà")
                else:
                    # Prétraiter et prédire
                    nouveau_client = pd.DataFrame([{
                        'client_id': client_id,
                        'client_type': client_type,
                        'age': age,
                        'annual_income': annual_income,
                        'loan_amount': loan_amount,
                        'loan_duration_months': loan_duration,
                        'interest_rate': interest_rate,
                        'past_defaults': past_defaults,
                        'credit_history_years': credit_history_years,
                        'existing_loans': existing_loans,
                        'monthly_payment_ratio': monthly_payment_ratio,
                        'collateral_value': collateral_value,
                        'sector': secteur,
                        'country': pays,
                        'days_late_avg': days_late_avg
                    }])
                    
                    X_nouveau = preprocesser_pour_modele(nouveau_client)
                    X_nouveau = X_nouveau.reindex(columns=X.columns, fill_value=0)
                    score_pred = model.predict(X_nouveau)[0]
                    solvency_score = float(score_pred)
                    
                    # Insérer dans la base
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO clients (
                            client_id, client_type, age, annual_income, loan_amount,
                            loan_duration_months, interest_rate, past_defaults,
                            credit_history_years, existing_loans, monthly_payment_ratio,
                            collateral_value, sector, country, days_late_avg, solvency_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        client_id, client_type, age, annual_income, loan_amount,
                        loan_duration, interest_rate, past_defaults,
                        credit_history_years, existing_loans, monthly_payment_ratio,
                        collateral_value, secteur, pays, days_late_avg, solvency_score
                    ))
                    conn.commit()
                    conn.close()
                    
                    categorie, couleur, decision = categorie_du_score(solvency_score)
                    
                    st.session_state["message_succes"] = f"✅ Client {client_id} ajouté avec succès !"
                    st.balloons()
                    
                    st.markdown(f"""
                    <div style="background:white;padding:20px;border-radius:16px;border-left:6px solid {couleur};box-shadow:0 4px 20px rgba(0,0,0,0.06);margin-top:12px;">
                        <h3>📊 Score prédit</h3>
                        <div style="font-size:2.5em;font-weight:900;color:{couleur};">{solvency_score:.0f}</div>
                        <div style="font-weight:700;color:{couleur};">{categorie}</div>
                        <div style="color:#64748b;">{decision}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.cache_resource.clear()
                    st.rerun()
    
    # ─── TAB 2 : CONSULTER LES CLIENTS ──────────────────────────────────────
    with tab_consulter:
        st.markdown("### 📋 Liste des clients")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            pays_f = st.selectbox("Filtrer par pays", ["Tous"] + sorted(df_brut['country'].unique().tolist()), key="filtre_pays")
        with col_f2:
            secteur_f = st.selectbox("Filtrer par secteur", ["Tous"] + sorted(df_brut['sector'].unique().tolist()), key="filtre_secteur")
        
        df_filtre = filtrer_clients(
            pays=pays_f if pays_f != "Tous" else None,
            secteur=secteur_f if secteur_f != "Tous" else None
        )
        
        st.dataframe(
            df_filtre[['client_id', 'client_type', 'country', 'sector', 'solvency_score']],
            use_container_width=True,
            height=400
        )
        st.caption(f"📊 {len(df_filtre)} clients affichés")
    
    # ─── TAB 3 : MODIFIER UN CLIENT ─────────────────────────────────────────
    with tab_modifier:
        st.markdown("### ✏️ Modifier un client")

        clients_list = df_brut['client_id'].tolist()
        client_a_modifier = st.selectbox(
            "Sélectionner le client à modifier",
            clients_list,
            key="modifier_select"
        )

        if client_a_modifier:
            idx_modif = df_brut[df_brut['client_id'] == client_a_modifier].index[0]
            row_modif = df_brut.iloc[idx_modif]

            with st.form("form_modifier_client"):

                col_m1, col_m2, col_m3 = st.columns(3)

                with col_m1:
                    age_m = st.number_input(
                        "Âge",
                        min_value=18,
                        max_value=100,
                        value=int(row_modif['age'])
                    )

                    client_type_m = st.selectbox(
                        "Type de client",
                        ["Personne_physique", "Personne_morale"],
                        index=0 if row_modif['client_type'] == 'Personne_physique' else 1
                    )

                with col_m2:
                    pays_m = st.selectbox(
                        "Pays",
                        ["Cameroun", "Congo", "Gabon", "Tchad"],
                        index=["Cameroun", "Congo", "Gabon", "Tchad"].index(row_modif['country'])
                    )

                    secteur_m = st.selectbox(
                        "Secteur",
                        ["Agriculture", "Commerce", "Industrie", "Services", "Transport"],
                        index=["Agriculture", "Commerce", "Industrie", "Services", "Transport"].index(row_modif['sector'])
                    )

                with col_m3:
                    annual_income_m = st.number_input(
                        "Revenu annuel",
                        min_value=100000,
                        max_value=50000000,
                        value=int(row_modif['annual_income']),
                        step=100000
                    )

                    loan_amount_m = st.number_input(
                        "Montant du crédit",
                        min_value=500000,
                        max_value=20000000,
                        value=int(row_modif['loan_amount']),
                        step=100000
                    )

                col_m4, col_m5, col_m6 = st.columns(3)

                with col_m4:
                    past_defaults_m = st.number_input(
                        "Défauts passés",
                        min_value=0,
                        max_value=5,
                        value=int(row_modif['past_defaults'])
                    )

                    days_late_avg_m = st.number_input(
                        "Retard moyen (jours)",
                        min_value=0.0,
                        max_value=120.0,
                        value=float(row_modif['days_late_avg'])
                    )

                with col_m5:
                    monthly_payment_ratio_m = st.number_input(
                        "Ratio mensualité/revenu",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(row_modif['monthly_payment_ratio']),
                        step=0.01
                    )

                    credit_history_years_m = st.number_input(
                        "Ancienneté crédit",
                        min_value=0,
                        max_value=30,
                        value=int(row_modif['credit_history_years'])
                    )

                with col_m6:
                    collateral_value_m = st.number_input(
                        "Valeur de la garantie",
                        min_value=0,
                        max_value=50000000,
                        value=int(row_modif['collateral_value']),
                        step=100000
                    )

                    existing_loans_m = st.number_input(
                        "Crédits en cours",
                        min_value=0,
                        max_value=10,
                        value=int(row_modif['existing_loans'])
                    )

                submitted_modif = st.form_submit_button(
                    "💾 Mettre à jour le client",
                    use_container_width=True
                )

                if submitted_modif:

                    conn = get_db_connection()
                    cursor = conn.cursor()

                    cursor.execute("""
                        UPDATE clients SET
                            client_type = ?,
                            age = ?,
                            annual_income = ?,
                            loan_amount = ?,
                            loan_duration_months = ?,
                            interest_rate = ?,
                            past_defaults = ?,
                            credit_history_years = ?,
                            existing_loans = ?,
                            monthly_payment_ratio = ?,
                            collateral_value = ?,
                            sector = ?,
                            country = ?,
                            days_late_avg = ?
                        WHERE client_id = ?
                    """, (
                        str(client_type_m),
                        int(age_m),
                        float(annual_income_m),
                        float(loan_amount_m),

                        int(row_modif['loan_duration_months']),
                        float(row_modif['interest_rate']),

                        int(past_defaults_m),
                        int(credit_history_years_m),
                        int(existing_loans_m),

                        float(monthly_payment_ratio_m),
                        float(collateral_value_m),

                        str(secteur_m),
                        str(pays_m),

                        float(days_late_avg_m),

                        str(client_a_modifier)
                    ))

                    conn.commit()
                    conn.close()

                    st.session_state["message_succes"] = (
                        f"✅ Client {client_a_modifier} mis à jour avec succès !"
                    )

                    st.cache_resource.clear()
                    st.rerun()
    
    # ─── TAB 4 : SUPPRIMER UN CLIENT ────────────────────────────────────────
    with tab_supprimer:
        st.markdown("### 🗑️ Supprimer un client")
        
        st.warning("⚠️ Cette action est irréversible. Êtes-vous sûr de vouloir supprimer un client ?")
        
        clients_list_del = df_brut['client_id'].tolist()
        client_a_supprimer = st.selectbox("Sélectionner le client à supprimer", clients_list_del, key="supprimer_select")
        
        if client_a_supprimer:
            row_del = df_brut[df_brut['client_id'] == client_a_supprimer].iloc[0]
            
            st.markdown(f"""
            <div style="background:#fef2f2;padding:16px;border-radius:12px;border:1px solid #fecaca;margin-bottom:12px;">
                <b>Client :</b> {client_a_supprimer}<br>
                <b>Pays :</b> {row_del['country']}<br>
                <b>Secteur :</b> {row_del['sector']}<br>
                <b>Score :</b> {row_del['solvency_score']:.0f}
            </div>
            """, unsafe_allow_html=True)
            
            col_conf1, col_conf2 = st.columns(2)
            with col_conf1:
                if st.button("🗑️ Confirmer la suppression", use_container_width=True, key="btn_delete"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM clients WHERE client_id = ?", (client_a_supprimer,))
                    conn.commit()
                    conn.close()
                    
                    st.session_state["message_succes"] = f"✅ Client {client_a_supprimer} supprimé avec succès !"
                    st.cache_resource.clear()
                    st.rerun()
            
            with col_conf2:
                if st.button("❌ Annuler", use_container_width=True):
                    st.info("Suppression annulée")



# ============================================================
# 8. PAGE : TABLEAU DE BORD (INGÉNIERIE FINTECH / BI-ENGINE ELEVATED)
# ============================================================
elif page == "📊 Tableau de bord":
    st.markdown("""
    <style>
        .block-container {
            padding: 2.5rem 3.5rem !important;
            background-color: #fafbfc !important;
        }
        .bi-banner-premium {
            background: linear-gradient(135deg, #091e42 0%, #17408b 100%);
            padding: 32px 40px;
            border-radius: 16px;
            color: white;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 24px;
            box-shadow: 0 12px 32px rgba(9, 30, 66, 0.12);
        }
        .bi-banner-icon {
            width: 56px;
            height: 56px;
            background: #ffffff;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.7rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        }
        .bi-banner-text h1 {
            color: white !important;
            margin: 0 !important;
            font-size: 2.1rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
        }
        .bi-banner-text p {
            color: rgba(255, 255, 255, 0.85);
            margin: 4px 0 0 0;
            font-size: 0.95rem;
        }
        .kpi-bi-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #eef2f6;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.01);
            display: flex;
            align-items: center;
            gap: 16px;
            height: 100%;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .kpi-bi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(9, 30, 66, 0.03);
        }
        .kpi-bi-icon {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            flex-shrink: 0;
        }
        .kpi-bi-meta {
            display: flex;
            flex-direction: column;
        }
        .kpi-bi-label {
            font-size: 0.75rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }
        .kpi-bi-val {
            font-size: 2rem;
            font-weight: 800;
            color: #090d16;
            line-height: 1.1;
            margin-top: 2px;
            letter-spacing: -0.5px;
        }
        .kpi-bi-sub {
            font-size: 0.75rem;
            color: #94a3b8;
            margin-top: 4px;
        }
        .bi-workspace-panel {
            background: #ffffff;
            border-radius: 20px;
            border: 1px solid #eef2f6;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.008);
            margin-top: 16px;
        }
        .bi-panel-header {
            margin-bottom: 24px;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 16px;
        }
        .bi-panel-title {
            font-size: 1.1rem;
            font-weight: 800;
            color: #090d16;
            letter-spacing: -0.2px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .bi-panel-subtitle {
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 2px;
        }
        div[data-testid="stTabs"] button {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            padding: 10px 20px !important;
            color: #475569 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stTabs"] button:hover {
            color: #090d16 !important;
            background: rgba(9, 30, 66, 0.03) !important;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #17408b !important;
            font-weight: 700 !important;
            background: rgba(23, 64, 139, 0.04) !important;
            box-shadow: inset 0 -2px 0 #17408b !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 1. BANNIÈRE
    st.markdown("""
    <div class="bi-banner-premium">
        <div class="bi-banner-icon">📈</div>
        <div class="bi-banner-text">
            <h1>Tableau de bord</h1>
            <p>Analyse du portefeuille ACREMAC</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not CHARGEMENT_OK:
        st.error(f"❌ Erreur critique d'infrastructure : {ERREUR}")
        st.stop()

    # Calcul des KPIs
    total_clients = len(df_brut)
    score_moyen = y_pred.mean() if len(y_pred) > 0 else 0
    score_min   = y_pred.min()  if len(y_pred) > 0 else 0
    score_max   = y_pred.max()  if len(y_pred) > 0 else 0

    # 2. KPIs
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-bi-card">
            <div class="kpi-bi-icon" style="background: rgba(9, 30, 66, 0.05); color: #091e42;">👥</div>
            <div class="kpi-bi-meta">
                <div class="kpi-bi-label">Clients Analysés</div>
                <div class="kpi-bi-val">{total_clients:,}</div>
                <div class="kpi-bi-sub">Total du portefeuille</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-bi-card">
            <div class="kpi-bi-icon" style="background: rgba(16, 185, 129, 0.08); color: #10b981;">📈</div>
            <div class="kpi-bi-meta">
                <div class="kpi-bi-label">Score Moyen Global</div>
                <div class="kpi-bi-val" style="color: #10b981;">{score_moyen:.0f}<span style="font-size:0.95rem;font-weight:600;"> pts</span></div>
                <div class="kpi-bi-sub">Score de crédit moyen</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-bi-card">
            <div class="kpi-bi-icon" style="background: rgba(245, 158, 11, 0.08); color: #f59e0b;">📉</div>
            <div class="kpi-bi-meta">
                <div class="kpi-bi-label">Score Minimum</div>
                <div class="kpi-bi-val" style="color: #f59e0b;">{score_min:.0f}</div>
                <div class="kpi-bi-sub">Score minimum observé</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-bi-card">
            <div class="kpi-bi-icon" style="background: rgba(29, 75, 138, 0.08); color: #1d4b88;">📊</div>
            <div class="kpi-bi-meta">
                <div class="kpi-bi-label">Score Maximum</div>
                <div class="kpi-bi-val" style="color: #1d4b88;">{score_max:.0f}</div>
                <div class="kpi-bi-sub">Score maximum observé</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── BATCH PREDICTION ────────────────────────────────────────────────────
    with st.expander("📤 Importation par lot (Batch Prediction)"):
        st.markdown("""
        <div style="background:#f0fdf4;padding:16px;border-radius:12px;border:1px solid #a7f3d0;margin-bottom:12px;">
            <b style="color:#059669;">📌 Format attendu :</b> Fichier CSV avec les mêmes colonnes que le dataset ACREMAC
        </div>
        """, unsafe_allow_html=True)

        fichier_batch = st.file_uploader("Importer un fichier CSV", type=['csv'], key="batch_upload")

        if fichier_batch is not None:
            df_batch = pd.read_csv(fichier_batch)
            st.dataframe(df_batch.head(), use_container_width=True)
            st.caption(f"📊 {len(df_batch)} clients à analyser")

            if st.button("🚀 Lancer la prédiction par lot"):
                with st.spinner(f"Analyse de {len(df_batch)} clients en cours..."):
                    df_batch_prep = df_batch.copy()
                    if 'client_id' in df_batch_prep.columns:
                        df_batch_prep = df_batch_prep.drop(columns=['client_id'])
                    if 'solvency_score' in df_batch_prep.columns:
                        df_batch_prep = df_batch_prep.drop(columns=['solvency_score'])

                    df_batch_prep['client_type'] = (df_batch_prep['client_type'] == 'Personne_physique').astype(int)
                    df_batch_prep = pd.get_dummies(df_batch_prep, columns=['sector', 'country'], drop_first=True)

                    for col in X.columns:
                        if col not in df_batch_prep.columns:
                            df_batch_prep[col] = 0
                    df_batch_prep = df_batch_prep[X.columns]

                    predictions = model.predict(df_batch_prep)

                    df_batch['Score_prédit'] = predictions.round(0).astype(int)
                    df_batch['Catégorie']    = [categorie_du_score(s)[0] for s in predictions]
                    df_batch['Décision']     = [categorie_du_score(s)[2] for s in predictions]

                    st.success(f"✅ {len(df_batch)} clients analysés avec succès !")
                    st.dataframe(df_batch, use_container_width=True)

                    csv_result = df_batch.to_csv(index=False)
                    st.download_button(
                        "📥 Télécharger les résultats (CSV)",
                        csv_result,
                        file_name="batch_predictions.csv",
                        mime="text/csv"
                    )

    # ── ALERTES CLIENTS À RISQUE ─────────────────────────────────────────────
    with st.expander("🚨 Alertes clients à risque"):
        base        = os.path.dirname(os.path.abspath(__file__))
        alert_path  = os.path.join(base, '..', 'logs', 'alertes.csv')

        if os.path.exists(alert_path):
            df_alert = pd.read_csv(alert_path)
            df_alert = df_alert.sort_values('date', ascending=False)
            st.dataframe(df_alert, use_container_width=True)
            st.caption(f"📊 {len(df_alert)} alertes enregistrées")

            if st.button("🔄 Vérifier les clients à risque maintenant"):
                verifier_clients_risques()
                st.success("✅ Vérification terminée")
                st.rerun()
        else:
            st.info("ℹ️ Aucune alerte enregistrée")

    # 3. ONGLETS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Liste des clients",
        "🌍 Statistiques",
        "📊 Catégories",
        "📈 Monitoring",
        "📊 Dashboard avancé"
    ])

    # ──────────────────────────────────────────────────────────
    # ONGLET 1 : LISTE DES CLIENTS
    # ──────────────────────────────────────────────────────────
    with tab1:
        st.markdown("""
        <div class="bi-workspace-panel">
            <div class="bi-panel-header">
                <div class="bi-panel-title">📋 Registre Centralisé du Portefeuille</div>
                <div class="bi-panel-subtitle">Base de données filtrable pour l'analyse granulaire des comptes de tiers.</div>
            </div>
        """, unsafe_allow_html=True)

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            pays = st.selectbox(
                "Sélectionner un territoire",
                ["Tous les pays"] + sorted(df_brut['country'].unique().tolist())
            )
        with col_f2:
            secteur = st.selectbox(
                "Sélectionner un secteur industriel",
                ["Tous les secteurs"] + sorted(df_brut['sector'].unique().tolist())
            )

        df_filtre = filtrer_clients(
            pays=pays       if pays    != "Tous les pays"     else None,
            secteur=secteur if secteur != "Tous les secteurs" else None
        )

        st.dataframe(
            df_filtre[['client_id', 'client_type', 'country', 'sector', 'solvency_score']].rename(
                columns={
                    'client_id':      'Client ID',
                    'client_type':    'Type de client',
                    'country':        'Pays',
                    'sector':         'Secteur',
                    'solvency_score': 'Score de solvabilité'
                }
            ),
            use_container_width=True,
            height=340
        )
        st.caption(f"💡 Affichage de **{len(df_filtre)}** entités correspondantes aux critères actifs.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # ONGLET 2 : STATISTIQUES PAR PAYS
    # ──────────────────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div class="bi-workspace-panel">
            <div class="bi-panel-header">
                <div class="bi-panel-title">🌍 Performance et Solvabilité par Pays</div>
                <div class="bi-panel-subtitle">Mesure comparative des indices de solvabilité moyens par zone géographique.</div>
            </div>
        """, unsafe_allow_html=True)

        df_pays = get_stats_pays()
        grid_t2_left, grid_t2_right = st.columns([1, 1.2])

        with grid_t2_left:
            st.markdown("<p style='font-size:0.75rem;font-weight:700;color:#64748b;text-transform:uppercase;margin-bottom:12px;'>Données d'évaluation</p>", unsafe_allow_html=True)
            st.dataframe(df_pays, use_container_width=True, height=260)

        with grid_t2_right:
            fig_p, ax_p = plt.subplots(figsize=(6, 3), dpi=140)
            fig_p.patch.set_facecolor('#ffffff')
            ax_p.set_facecolor('#ffffff')

            colors_p = ['#091e42', '#10b981', '#f59e0b', '#ef4444']
            bars = ax_p.bar(
                df_pays['country'], df_pays['score_moyen'],
                color=colors_p[:len(df_pays)], width=0.42, edgecolor='none', zorder=3
            )

            ax_p.spines['top'].set_visible(False)
            ax_p.spines['right'].set_visible(False)
            ax_p.spines['left'].set_visible(False)
            ax_p.spines['bottom'].set_color('#e2e8f0')
            ax_p.tick_params(colors='#64748b', labelsize=8, length=0)
            ax_p.yaxis.grid(True, linestyle=':', alpha=0.5, color='#cbd5e1', zorder=0)

            for bar, val in zip(bars, df_pays['score_moyen']):
                ax_p.text(
                    bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 20,
                    f'{val:.0f}',
                    ha='center', va='bottom', fontsize=8, color='#090d16', fontweight='bold'
                )

            ax_p.set_ylim(0, 1000)
            st.pyplot(fig_p)
            plt.close(fig_p)

        st.markdown('</div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # ONGLET 3 : CATÉGORIES — DONUT
    # ──────────────────────────────────────────────────────────
    with tab3:
        st.markdown("""
        <div class="bi-workspace-panel">
            <div class="bi-panel-header">
                <div class="bi-panel-title">📊 Segmentation par Profil et Classes de Risques</div>
                <div class="bi-panel-subtitle">Répartition volumétrique du portefeuille global selon la taxonomie ACREMAC.</div>
            </div>
        """, unsafe_allow_html=True)

        df_cat = get_stats_categorie()
        grid_t3_left, grid_t3_right = st.columns([1, 1.2])

        with grid_t3_left:
            st.markdown("<p style='font-size:0.75rem;font-weight:700;color:#64748b;text-transform:uppercase;margin-bottom:12px;'>Volumes par catégorie</p>", unsafe_allow_html=True)
            st.dataframe(df_cat, use_container_width=True, height=260)

        with grid_t3_right:
            couleurs_strictes = {
                'Excellent': '#10b981',
                'Bon':       '#17408b',
                'Moyen':     '#f59e0b',
                'Risqué':    '#ef4444'
            }
            liste_couleurs_ordonnee = [couleurs_strictes.get(cat, '#cbd5e1') for cat in df_cat['categorie']]

            fig_c, ax_c = plt.subplots(figsize=(6, 3.2), dpi=140)
            fig_c.patch.set_facecolor('#ffffff')

            wedges, texts, autotexts = ax_c.pie(
                df_cat['nb_clients'],
                labels=df_cat['categorie'],
                autopct='%1.1f%%',
                startangle=140,
                colors=liste_couleurs_ordonnee,
                pctdistance=0.72,
                textprops=dict(color="#090d16", fontsize=8.5, fontweight='500'),
                wedgeprops=dict(width=0.38, edgecolor='white', linewidth=3)
            )

            for i, wedge in enumerate(wedges):
                categorie_nom = df_cat['categorie'].iloc[i]
                autotexts[i].set_color('white')
                autotexts[i].set_fontsize(7.5)
                autotexts[i].set_weight('700')

                if categorie_nom == 'Moyen':
                    import numpy as np
                    angle = (wedge.theta2 + wedge.theta1) / 2.0
                    r = 0.78
                    x = r * np.cos(np.deg2rad(angle))
                    y = r * np.sin(np.deg2rad(angle))
                    autotexts[i].set_position((x, y))

            ax_c.axis('equal')
            st.pyplot(fig_c)
            plt.close(fig_c)

        st.markdown('</div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # ONGLET 4 : MONITORING DES PERFORMANCES DU MODÈLE
    # ──────────────────────────────────────────────────────────
    with tab4:
        st.markdown("""
        <div class="bi-workspace-panel">
            <div class="bi-panel-header">
                <div class="bi-panel-title">📈 Suivi des performances du modèle</div>
                <div class="bi-panel-subtitle">Évolution des métriques clés dans le temps</div>
            </div>
        """, unsafe_allow_html=True)

        # BLOC EXPLICATIF MONITORING
        st.markdown("""
        <div style="background:#f0f9ff;padding:16px 20px;border-radius:12px;border:1px solid #bae6fd;margin-bottom:20px;">
            <b style="color:#0369a1;">📌 À quoi sert cet onglet ?</b>
            <p style="color:#475569;margin:6px 0 0 0;font-size:0.9em;line-height:1.5;">
                Cet onglet permet de <b>surveiller la stabilité et la performance du modèle</b>
                dans le temps. Les métriques affichées (R², RMSE, MAE) indiquent si le modèle
                reste fiable ou s'il commence à perdre en précision.
            </p>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px;">
                <div style="background:white;padding:10px 14px;border-radius:10px;border-left:3px solid #10b981;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                    <b style="color:#059669;font-size:0.95rem;">R²</b>
                    <span style="font-size:0.8em;color:#64748b;display:block;margin-top:3px;">Plus il est proche de 1, meilleur est le modèle</span>
                </div>
                <div style="background:white;padding:10px 14px;border-radius:10px;border-left:3px solid #f59e0b;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                    <b style="color:#d97706;font-size:0.95rem;">RMSE</b>
                    <span style="font-size:0.8em;color:#64748b;display:block;margin-top:3px;">Erreur quadratique moyenne (en points)</span>
                </div>
                <div style="background:white;padding:10px 14px;border-radius:10px;border-left:3px solid #3b82f6;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                    <b style="color:#2563eb;font-size:0.95rem;">MAE</b>
                    <span style="font-size:0.8em;color:#64748b;display:block;margin-top:3px;">Erreur absolue moyenne (en points)</span>
                </div>
            </div>
            <div style="margin-top:10px;padding:8px 12px;background:rgba(3,105,161,0.05);border-radius:8px;font-size:0.85em;color:#64748b;">
                💡 <b>Conseil :</b> Si le R² descend sous <b style="color:#0369a1;">0.90</b>, un réentraînement du modèle est recommandé.
            </div>
        </div>
        """, unsafe_allow_html=True)

        def get_historique_performances():
            base      = os.path.dirname(os.path.abspath(__file__))
            hist_path = os.path.join(base, '..', 'models', 'historique_performances.csv')
            if os.path.exists(hist_path):
                return pd.read_csv(hist_path)
            else:
                df_hist = pd.DataFrame({
                    'date': [pd.Timestamp.now().strftime('%Y-%m-%d')],
                    'r2':   [0.9449],
                    'rmse': [13.51],
                    'mae':  [9.76]
                })
                os.makedirs(os.path.dirname(hist_path), exist_ok=True)
                df_hist.to_csv(hist_path, index=False)
                return df_hist

        def ajouter_performance(date, r2, rmse, mae):
            base      = os.path.dirname(os.path.abspath(__file__))
            hist_path = os.path.join(base, '..', 'models', 'historique_performances.csv')
            df_hist   = get_historique_performances()
            nouvelle_ligne = pd.DataFrame({
                'date': [date],
                'r2':   [r2],
                'rmse': [rmse],
                'mae':  [mae]
            })
            df_hist = pd.concat([df_hist, nouvelle_ligne], ignore_index=True)
            df_hist.to_csv(hist_path, index=False)
            return df_hist

        df_hist  = get_historique_performances()
        derniere = df_hist.iloc[-1]

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("R² actuel",                 f"{derniere['r2']:.4f}",  delta="0.0000")
        col_m2.metric("RMSE actuel",               f"{derniere['rmse']:.2f}", delta="0.00")
        col_m3.metric("MAE actuel",                f"{derniere['mae']:.2f}",  delta="0.00")
        col_m4.metric("Date dernière mise à jour",  derniere['date'])

        fig_m, ax_m = plt.subplots(figsize=(10, 4))
        ax_m.plot(df_hist['date'], df_hist['r2'], marker='o', color='#10b981', linewidth=2, label='R²')
        ax_m.set_ylabel('R²')
        ax_m.set_xlabel('Date')
        ax_m.set_title('Évolution du R² dans le temps')
        ax_m.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig_m)
        plt.close()

        if st.button("🔄 Évaluer les performances actuelles"):
            from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
            import numpy as np

            # ✅ CORRECTION : y_true extrait directement depuis df_brut
            y_true        = df_brut['solvency_score'].values
            y_pred_actuel = model.predict(X)

            if len(y_true) != len(y_pred_actuel):
                st.error(
                    f"❌ Incohérence de dimensions : "
                    f"{len(y_true)} valeurs réelles vs {len(y_pred_actuel)} prédictions."
                )
            else:
                r2_actuel   = r2_score(y_true, y_pred_actuel)
                rmse_actuel = np.sqrt(mean_squared_error(y_true, y_pred_actuel))
                mae_actuel  = mean_absolute_error(y_true, y_pred_actuel)

                date_actuelle = pd.Timestamp.now().strftime('%Y-%m-%d')
                ajouter_performance(date_actuelle, r2_actuel, rmse_actuel, mae_actuel)

                st.success(
                    f"✅ Évaluation du {date_actuelle} : "
                    f"R²={r2_actuel:.4f} | RMSE={rmse_actuel:.2f} | MAE={mae_actuel:.2f}"
                )
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # ONGLET 5 : DASHBOARD AVANCÉ — VISUALISATIONS PLOTLY
    # ──────────────────────────────────────────────────────────
    with tab5:
        st.markdown("""
        <div class="bi-workspace-panel">
            <div class="bi-panel-header">
                <div class="bi-panel-title">📊 Dashboard avancé</div>
                <div class="bi-panel-subtitle">Visualisations interactives du portefeuille</div>
            </div>
        """, unsafe_allow_html=True)

        # BLOC EXPLICATIF DASHBOARD AVANCÉ
        st.markdown("""
        <div style="background:#f0fdf4;padding:16px 20px;border-radius:12px;border:1px solid #bbf7d0;margin-bottom:20px;">
            <b style="color:#16a34a;">📌 À quoi sert cet onglet ?</b>
            <p style="color:#475569;margin:6px 0 0 0;font-size:0.9em;line-height:1.5;">
                Cet onglet propose des <b>visualisations interactives</b> pour explorer les données
                sous différents angles. Il permet d'identifier des tendances, des corrélations
                et des patterns qui ne sont pas visibles dans les tableaux classiques.
            </p>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px;">
                <div style="background:white;padding:10px 14px;border-radius:10px;border-left:3px solid #8b5cf6;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                    <b style="color:#7c3aed;font-size:0.95rem;">🔗 Matrice de corrélation</b>
                    <span style="font-size:0.8em;color:#64748b;display:block;margin-top:3px;">Relations entre les variables</span>
                </div>
                <div style="background:white;padding:10px 14px;border-radius:10px;border-left:3px solid #f97316;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                    <b style="color:#ea580c;font-size:0.95rem;">📈 Âge vs Score</b>
                    <span style="font-size:0.8em;color:#64748b;display:block;margin-top:3px;">Influence de l'âge sur la solvabilité</span>
                </div>
                <div style="background:white;padding:10px 14px;border-radius:10px;border-left:3px solid #06b6d4;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                    <b style="color:#0891b2;font-size:0.95rem;">🌍 Distribution par pays</b>
                    <span style="font-size:0.8em;color:#64748b;display:block;margin-top:3px;">Répartition géographique des clients</span>
                </div>
            </div>
            <div style="margin-top:10px;padding:8px 12px;background:rgba(22,163,74,0.05);border-radius:8px;font-size:0.85em;color:#64748b;">
                💡 <b>Conseil :</b> Passez la souris sur les graphiques pour voir les valeurs détaillées.
            </div>
        </div>
        """, unsafe_allow_html=True)

        import plotly.express as px
        import plotly.graph_objects as go
        import numpy as np

        st.markdown("#### 🔗 Matrice de corrélation des variables")
        corr_matrix = df_brut.select_dtypes(include=[np.number]).corr()
        fig_corr = px.imshow(
            corr_matrix, text_auto=True, aspect="auto",
            color_continuous_scale='RdBu_r'
        )
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("#### 📈 Distribution Âge vs Score")
        fig_scatter = px.scatter(
            df_brut, x='age', y='solvency_score',
            color='sector', hover_data=['client_id'],
            title="Âge vs Score de solvabilité par secteur"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("#### 🌍 Distribution par pays")
        fig_pays_adv = px.bar(
            df_brut.groupby('country').size().reset_index(name='count'),
            x='country', y='count', color='country',
            title="Nombre de clients par pays"
        )
        st.plotly_chart(fig_pays_adv, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)








# ============================================================
# PAGE : ANALYSE CLIENT (FINTECH REPLICA DESIGN - FULL)
# ============================================================
elif page == "👤 Analyse client":

    # ── Palette ACREMAC ──────────────────────────────────────
    ACREMAC_COLORS = {
        "primary":   "#0d1f3c",
        "secondary": "#1a5fa0",
        "accent":    "#D8A03F",
        "success":   "#10b981",
        "warning":   "#f59e0b",
        "danger":    "#ef4444",
        "info":      "#8b5cf6",
        "light":     "#f8fafc",
        "dark":      "#0a1628",
    }

    # ── Traduction des variables SHAP ────────────────────────
    SHAP_VAR_TRANSLATION = {
        "past_defaults":          "Nombre de défauts de paiement",
        "days_late_avg":          "Jours de retard moyen",
        "monthly_payment_ratio":  "Ratio mensualité / revenu",
        "annual_income":          "Revenu annuel",
        "credit_history_years":   "Ancienneté du crédit",
        "loan_amount":            "Montant du crédit",
        "loan_duration_months":   "Durée du crédit (mois)",
        "interest_rate":          "Taux d'intérêt",
        "existing_loans":         "Crédits en cours",
        "collateral_value":       "Valeur de la garantie",
        "age":                    "Âge du client",
        "client_type":            "Type de client",
        "sector_Commerce":        "Secteur Commerce",
        "sector_Industrie":       "Secteur Industrie",
        "sector_Services":        "Secteur Services",
        "sector_Transport":       "Secteur Transport",
        "country_Congo":          "Pays Congo",
        "country_Gabon":          "Pays Gabon",
        "country_Tchad":          "Pays Tchad",
    }

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

        /* ── Base ─────────────────────────────────────────── */
        .block-container { padding: 2.5rem 3.5rem !important; background-color: #fafbfc !important; }

        /* ── En-tête ───────────────────────────────────────── */
        .analysis-title-box          { display:flex; align-items:center; gap:16px; }
        .analysis-icon-badge         { width:56px; height:56px; background:#f0f4f8; color:#1d4b88; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:1.8rem; }
        .analysis-title-box h1       { color:#091e42!important; margin:0!important; font-size:2.1rem!important; font-weight:800!important; letter-spacing:-0.5px; }
        .analysis-title-box p        { color:#64748b; margin:4px 0 0 0; font-size:0.95rem; }

        /* ── Carte score ────────────────────────────────────── */
        .score-display-card          { background:#ffffff; border-radius:16px; padding:28px; border:1px solid #eef2f6; box-shadow:0 4px 12px rgba(0,0,0,.04); height:100%; }
        .score-inner-flex            { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:24px; }
        .score-title-label           { font-size:.85rem; font-weight:600; color:#64748b; }
        .score-big-number            { font-size:4rem; font-weight:800; line-height:1; margin:12px 0 6px 0; letter-spacing:-1px; }
        .score-max-boundary          { font-size:.95rem; color:#94a3b8; }

        /* ── Badge décision ─────────────────────────────────── */
        .decision-badge-container    { border-radius:12px; padding:14px 20px; display:flex; align-items:center; gap:12px; min-width:180px; }
        .decision-badge-icon         { font-size:1.5rem; display:flex; align-items:center; }
        .decision-badge-meta         { display:flex; flex-direction:column; }
        .decision-badge-title        { font-size:1.1rem; font-weight:700; line-height:1.2; }
        .decision-badge-desc         { font-size:.8rem; color:#64748b; margin-top:2px; }

        /* ── Barre de progression ───────────────────────────── */
        .progress-indicator-wrapper  { position:relative; margin:50px 0 25px 0; background:#e2e8f0; border-radius:30px; height:8px; }
        .progress-fill-bar           { height:100%; border-radius:30px; position:relative; }
        .progress-floating-pin       { position:absolute; right:0; top:-32px; transform:translateX(50%); color:white; font-size:.75rem; font-weight:700; padding:3px 8px; border-radius:4px; line-height:1; display:inline-flex; align-items:center; justify-content:center; white-space:nowrap; }
        .progress-floating-pin::after{ content:''; position:absolute; bottom:-4px; left:50%; transform:translateX(-50%); border-width:4px 4px 0; border-style:solid; border-color:inherit; display:block; width:0; }

        /* ── Profil client ──────────────────────────────────── */
        .profile-spec-card           { background:#ffffff; border-radius:16px; padding:28px; border:1px solid #eef2f6; box-shadow:0 4px 12px rgba(0,0,0,.04); height:100%; }
        .profile-spec-title          { font-size:.95rem; font-weight:700; color:#091e42; margin-bottom:20px; display:flex; align-items:center; gap:8px; }
        .profile-row-item            { display:flex; justify-content:space-between; align-items:center; padding:13px 0; border-bottom:1px solid #f1f5f9; font-size:.9rem; }
        .profile-row-item:last-child { border-bottom:none; }
        .profile-row-label           { color:#64748b; font-weight:500; }
        .profile-row-value           { color:#091e42; font-weight:600; display:flex; align-items:center; gap:8px; }
        .profile-flag-img            { width:22px; height:15px; object-fit:cover; border-radius:2px; box-shadow:0 1px 3px rgba(0,0,0,.1); display:inline-block; }

        /* ── Facteurs SHAP ──────────────────────────────────── */
        .factors-panel-container     { margin-top:35px; }
        .factors-section-title       { font-size:1rem; font-weight:700; margin-bottom:20px; display:flex; align-items:center; gap:8px; }
        .factor-item-premium         { background:#ffffff; border:1px solid #eef2f6; padding:14px 20px; border-radius:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; }
        .factor-left-meta            { display:flex; align-items:center; gap:14px; color:#334155; font-weight:600; font-size:.9rem; }
        .factor-mini-badge           { width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:1.1rem; }
        .factor-impact-value         { font-size:.95rem; font-weight:700; }

        /* ── Carte action SHAP ──────────────────────────────── */
        .trigger-action-card         { background:#ffffff; border-radius:16px; border:1px solid #eef2f6; padding:24px; margin-top:35px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 4px 12px rgba(0,0,0,.04); }
        .trigger-left-block          { display:flex; align-items:center; gap:16px; }
        .trigger-icon-container      { width:48px; height:48px; background:#eef2f6; color:#17408b; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.3rem; }
        .trigger-text-meta h4        { margin:0; font-size:1.1rem; font-weight:700; color:#091e42; }
        .trigger-text-meta p         { margin:4px 0 0 0; font-size:.85rem; color:#64748b; }

        /* ── Bouton fantôme ─────────────────────────────────── */
        .st-custom-btn-box           { position:relative; }
        .html-btn-replica            { background-color:#1d4b88; color:white; border:none; padding:12px 24px; border-radius:8px; font-weight:600; font-size:.9rem; display:flex; align-items:center; gap:10px; pointer-events:none; }
        .st-custom-btn-box div.stButton>button { position:absolute; top:0; left:0; width:100%; height:100%; opacity:0!important; cursor:pointer; z-index:10; }

        /* ── Onglets ────────────────────────────────────────── */
        div[data-baseweb="tab-list"] { gap:8px; }
        div[data-baseweb="tab"]      { border-radius:8px!important; padding:8px 16px!important; font-weight:600!important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Garde-fou chargement ─────────────────────────────────
    if not CHARGEMENT_OK:
        st.error(f"❌ Erreur critique : {ERREUR}")
        st.stop()

    # ── En-tête + sélecteur client ───────────────────────────
    col_header_title, col_header_select = st.columns([1.6, 1])

    with col_header_title:
        st.markdown("""
        <div class="analysis-title-box">
            <div class="analysis-icon-badge">👥</div>
            <div>
                <h1>Analyse individuelle</h1>
                <p>💡 Score, explication SHAP et simulation personnalisée</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_header_select:
        client_id = st.selectbox(
            "🔎 Choisir un client",
            df_brut['client_id'].tolist(),
            label_visibility="visible"
        )

    # ── Données du client sélectionné ───────────────────────
    idx  = df_brut[df_brut['client_id'] == client_id].index[0]
    row  = df_brut.iloc[idx]
    score = predire_score(model, X, idx)
    categorie, couleur, decision = categorie_du_score(score)

    # Tendance vs portefeuille
    moyenne_portefeuille = y_pred.mean()
    ecart_vs_moy         = score - moyenne_portefeuille
    tendance_icone       = "📈" if ecart_vs_moy > 0 else "📉"
    tendance_texte       = "Au-dessus de la moyenne du portefeuille" if ecart_vs_moy > 0 else "En dessous de la moyenne du portefeuille"

    # Fiabilité de prédiction
    confidence_score = 100 - (score - y_pred.mean()) / (y_pred.max() - y_pred.min()) * 30
    confidence_score = max(60, min(95, confidence_score))
    confidence_color = ACREMAC_COLORS["success"] if confidence_score > 75 else ACREMAC_COLORS["warning"]

    # Ancienneté normalisée pour la timeline
    anciennete_norm = min((row['credit_history_years'] / 20) * 100, 100)

    # Niveaux de risque
    niveaux_risque = {
        "Excellent": {"icon": "🟢", "label": "Risque très faible",  "bg": "rgba(16,185,129,0.12)"},
        "Bon":       {"icon": "🟡", "label": "Risque faible",       "bg": "rgba(245,158,11,0.12)"},
        "Moyen":     {"icon": "🟠", "label": "Risque modéré",       "bg": "rgba(249,115,22,0.12)"},
        "Risqué":    {"icon": "🔴", "label": "Risque élevé",        "bg": "rgba(239,68,68,0.12)"},
    }
    risque_info = niveaux_risque.get(categorie, niveaux_risque["Moyen"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # ONGLETS PRINCIPAUX
    # ════════════════════════════════════════════════════════
    onglet1, onglet2, onglet3 = st.tabs([
        "📊 Score & Profil",
        "🔍 SHAP & Facteurs",
        "📈 Analyse comparée"
    ])

    # ────────────────────────────────────────────────────────
    # ONGLET 1 — Score & Profil
    # ────────────────────────────────────────────────────────
    with onglet1:

        col_body_left, col_body_right = st.columns([1.25, 1])

        # ── Colonne gauche : carte score ─────────────────────
        with col_body_left:
            pct_bar         = max(0, min(100, ((score - 466) / (737 - 466)) * 100))
            risque_bg       = risque_info['bg']
            risque_icon     = risque_info['icon']
            risque_label    = risque_info['label']
            warn_color      = ACREMAC_COLORS['warning']

            # ── Carte score principale ────────────────────────
            st.markdown(
                f'<div class="score-display-card">'
                f'<div class="score-inner-flex">'
                f'<div>'
                f'<div class="score-title-label">💳 Score de solvabilité</div>'
                f'<div class="score-big-number" style="color:{couleur};">{score:.0f}</div>'
                f'<div class="score-max-boundary">/ 737 points</div>'
                f'</div>'
                f'<div class="decision-badge-container" style="background:{couleur}10; border:1px solid {couleur}30;">'
                f'<div class="decision-badge-icon">🛡️</div>'
                f'<div class="decision-badge-meta">'
                f'<div class="decision-badge-title" style="color:{couleur};">{categorie}</div>'
                f'<div class="decision-badge-desc">{decision}</div>'
                f'</div>'
                f'</div>'
                f'</div>'
                f'<div class="progress-indicator-wrapper">'
                f'<div class="progress-fill-bar" style="width:{pct_bar}%; background:{couleur};">'
                f'<div class="progress-floating-pin" style="background:{couleur}; border-color:{couleur};">{score:.0f}</div>'
                f'</div>'
                f'<div style="position:absolute; left:0; bottom:-22px; font-size:.8rem; color:#94a3b8; font-weight:500;">466</div>'
                f'<div style="position:absolute; right:0; bottom:-22px; font-size:.8rem; color:#94a3b8; font-weight:500;">737</div>'
                f'</div>'
                f'<div style="margin-top:28px;">'
                f'<div style="display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:50px; background:{risque_bg}; border:1px solid {couleur}40;">'
                f'<span style="font-size:1.1em;">{risque_icon}</span>'
                f'<span style="font-weight:600; color:{couleur}; font-size:.9rem;">{risque_label}</span>'
                f'</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # ── Fiabilité de prédiction ───────────────────────
            st.markdown(
                f'<div style="background:white; padding:14px 18px; border-radius:12px; border:1px solid #eef2f6; margin-top:14px;">'
                f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                f'<div>'
                f'<div style="font-size:.7em; color:#64748b;">🎯 Fiabilité de la prédiction</div>'
                f'<div style="font-size:1.3em; font-weight:800; color:#0d1f3c;">{confidence_score:.0f}%</div>'
                f'</div>'
                f'<div style="position:relative; width:130px; height:7px; background:#e2e8f0; border-radius:6px; overflow:hidden;">'
                f'<div style="width:{confidence_score}%; height:100%; background:linear-gradient(90deg,{warn_color},{confidence_color}); border-radius:6px;"></div>'
                f'</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # ── Tendance vs portefeuille ──────────────────────
            st.markdown(
                f'<div style="display:flex; align-items:center; gap:10px; background:#f8fafc; padding:10px 16px; border-radius:10px; border:1px solid #eef2f6; margin-top:10px;">'
                f'<span style="font-size:1.4em;">{tendance_icone}</span>'
                f'<span style="font-weight:500; color:#64748b; font-size:.9rem;">{tendance_texte}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        # ── Colonne droite : profil ──────────────────────────
        with col_body_right:

            # Drapeau
            pays_client   = row['country']
            nom_pays_norm = str(pays_client).lower()
            flag_url = ""
            if "cameroun"  in nom_pays_norm:              flag_url = "https://flagcdn.com/w40/cm.png"
            elif "ivoire"  in nom_pays_norm:              flag_url = "https://flagcdn.com/w40/ci.png"
            elif "sénégal" in nom_pays_norm or "senegal" in nom_pays_norm: flag_url = "https://flagcdn.com/w40/sn.png"
            elif "gabon"   in nom_pays_norm:              flag_url = "https://flagcdn.com/w40/ga.png"
            elif "rdc"     in nom_pays_norm or "congo" in nom_pays_norm:   flag_url = "https://flagcdn.com/w40/cd.png"
            elif "tchad"   in nom_pays_norm:              flag_url = "https://flagcdn.com/w40/td.png"
            flag_html = f'<img class="profile-flag-img" src="{flag_url}">' if flag_url else ""

            # Mini-carte identité
            st.markdown(f"""
            <div style="background:white; padding:16px; border-radius:12px;
                        border:1px solid #eef2f6; margin-bottom:12px;
                        box-shadow:0 2px 8px rgba(0,0,0,.03);">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="font-size:2.4em;">🏢</div>
                    <div>
                        <div style="font-weight:700; color:#0d1f3c; font-size:1em;">{client_id}</div>
                        <div style="font-size:.75em; color:#64748b;">{row.get('client_type','—')}</div>
                        <div style="font-size:.7em; color:#94a3b8; margin-top:2px;">📂 Secteur {row['sector']}</div>
                    </div>
                </div>
                <div style="display:flex; gap:16px; margin-top:10px; flex-wrap:wrap;">
                    <div style="font-size:.7em; color:#64748b;">🎂 {int(row['age'])} ans</div>
                    <div style="font-size:.7em; color:#64748b;">💼 {row['sector']}</div>
                    <div style="font-size:.7em; color:#64748b;">🏦 {int(row['credit_history_years'])} ans d'ancienneté</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Fiche profil détaillée
            st.markdown(f"""
            <div class="profile-spec-card">
                <div class="profile-spec-title">📋 Profil du client</div>
                <div class="profile-row-item">
                    <span class="profile-row-label">🪪 ID Client</span>
                    <span class="profile-row-value">{client_id}</span>
                </div>
                <div class="profile-row-item">
                    <span class="profile-row-label">🌍 Pays</span>
                    <span class="profile-row-value">{flag_html}{pays_client}</span>
                </div>
                <div class="profile-row-item">
                    <span class="profile-row-label">🏭 Secteur</span>
                    <span class="profile-row-value">{row['sector']}</span>
                </div>
                <div class="profile-row-item">
                    <span class="profile-row-label">⛔ Défauts passés</span>
                    <span class="profile-row-value">{int(row['past_defaults'])}</span>
                </div>
                <div class="profile-row-item">
                    <span class="profile-row-label">⏱️ Retard moyen</span>
                    <span class="profile-row-value" style="color:#17408b;">{row['days_late_avg']:.1f} jours</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Chronologie ──────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📅 Chronologie du client"):
            st.markdown(f"""
            <div style="background:white; padding:22px; border-radius:16px; border:1px solid #eef2f6;">
                <div style="font-weight:700; color:#0d1f3c; margin-bottom:16px; font-size:.95rem;">
                    ⏳ Historique de crédit
                </div>
                <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px;">
                    <div style="display:flex; flex-direction:column; align-items:center; gap:2px;">
                        <div style="font-size:.6em; color:#94a3b8;">Début</div>
                        <div style="font-size:1.2em; font-weight:700; color:#0d1f3c;">{int(row['credit_history_years'])} ans</div>
                    </div>
                    <div style="flex:1; height:5px; background:#e2e8f0; border-radius:4px; position:relative;">
                        <div style="width:{anciennete_norm}%; height:100%;
                                    background:linear-gradient(90deg,#1a5fa0,#10b981);
                                    border-radius:4px;"></div>
                        <div style="position:absolute; top:-6px; left:{anciennete_norm}%;
                                    transform:translateX(-50%);">
                            <div style="width:16px; height:16px; background:#1a5fa0; border-radius:50%;
                                        border:3px solid white; box-shadow:0 2px 8px rgba(0,0,0,.15);"></div>
                        </div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:center; gap:2px;">
                        <div style="font-size:.6em; color:#94a3b8;">Aujourd'hui</div>
                        <div style="font-size:1.2em; font-weight:700; color:#10b981;">✅</div>
                    </div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:.78em; color:#64748b;
                            background:#f8fafc; padding:10px 14px; border-radius:10px; flex-wrap:wrap; gap:8px;">
                    <span>📅 {int(row['credit_history_years'])} ans d'ancienneté</span>
                    <span>🏦 {int(row['existing_loans'])} crédit(s) en cours</span>
                    <span>⏳ {int(row['loan_duration_months'])} mois de durée</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Export ───────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📥 Exporter ce rapport")
        col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
        with col_exp1:
            st.download_button("📄 PDF",  "Contenu PDF",  file_name=f"rapport_{client_id}.pdf",  use_container_width=True)
        with col_exp2:
            st.download_button("📝 TXT",  "Contenu TXT",  file_name=f"rapport_{client_id}.txt",  use_container_width=True)
        with col_exp3:
            st.download_button("🔷 JSON", "Contenu JSON", file_name=f"rapport_{client_id}.json", use_container_width=True)
        with col_exp4:
            
            st.info("📄 PDF via ReportLab", icon="ℹ️")



    # ────────────────────────────────────────────────────────
    # ONGLET 2 — SHAP & Facteurs
    # ────────────────────────────────────────────────────────
    with onglet2:

        shap_client = shap_df.iloc[idx]
        top_pos = shap_client.sort_values(ascending=False).head(3)
        top_neg = shap_client.sort_values(ascending=True).head(3)

        icon_map = {
            'past_defaults':         '⚠️',
            'days_late_avg':         '⏰',
            'monthly_payment_ratio': '📊',
            'annual_income':         '💰',
            'credit_history_years':  '📅',
            'loan_amount':           '💳',
            'loan_duration_months':  '📆',
            'interest_rate':         '📈',
            'existing_loans':        '🏦',
            'collateral_value':      '🏠',
            'age':                   '🎂',
            'client_type':           '👤',
        }

        col_pos_panel, col_neg_panel = st.columns(2)

        with col_pos_panel:
            st.markdown('<div class="factors-panel-container">', unsafe_allow_html=True)
            st.markdown(
                '<div class="factors-section-title" style="color:#10b981;">✅ Facteurs favorables</div>',
                unsafe_allow_html=True
            )
            for var, val in top_pos.items():
                ico         = icon_map.get(var, '💹')
                label_clean = SHAP_VAR_TRANSLATION.get(var, str(var).replace('_', ' ').title())
                st.markdown(f"""
                <div class="factor-item-premium" style="border-left:4px solid #10b981;">
                    <div class="factor-left-meta">
                        <div class="factor-mini-badge" style="background:#eefdf5; color:#10b981;">{ico}</div>
                        <span>{label_clean}</span>
                    </div>
                    <div class="factor-impact-value" style="color:#10b981;">+{val:.2f} pts</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_neg_panel:
            st.markdown('<div class="factors-panel-container">', unsafe_allow_html=True)
            st.markdown(
                '<div class="factors-section-title" style="color:#ef4444;">🚨 Facteurs défavorables</div>',
                unsafe_allow_html=True
            )
            for var, val in top_neg.items():
                ico         = icon_map.get(var, '🚫')
                label_clean = SHAP_VAR_TRANSLATION.get(var, str(var).replace('_', ' ').title())
                st.markdown(f"""
                <div class="factor-item-premium" style="border-left:4px solid #ef4444;">
                    <div class="factor-left-meta">
                        <div class="factor-mini-badge" style="background:#fdf2f2; color:#ef4444;">{ico}</div>
                        <span>{label_clean}</span>
                    </div>
                    <div class="factor-impact-value" style="color:#ef4444;">{val:.2f} pts</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Bouton Waterfall ──────────────────────────────────
        st.markdown("""
        <div class="trigger-action-card">
            <div class="trigger-left-block">
                <div class="trigger-icon-container">📊</div>
                <div class="trigger-text-meta">
                    <h4>Visualisation SHAP</h4>
                    <p>Analyse détaillée des contributions des variables</p>
                </div>
            </div>
            <div class="st-custom-btn-box">
                <div class="html-btn-replica">
                    <span style="font-size:1.1rem;">📊</span> Afficher le graphique SHAP
                </div>
        """, unsafe_allow_html=True)

        if st.button("Afficher le graphique SHAP", key="btn_shap_trigger"):
            afficher_waterfall(idx, model, X, shap_df, base_value)

        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Simulation What-If ────────────────────────────────
        with st.expander("🔮 Analyse de sensibilité — Simulation « What-If »"):
            st.markdown("""
            <div style="background:#f0fdf4; padding:12px 16px; border-radius:12px;
                        border:1px solid #a7f3d0; margin-bottom:16px;">
                <b style="color:#059669;">💡 Simulez l'impact de modifications sur le score du client</b>
            </div>
            """, unsafe_allow_html=True)

            col_w1, col_w2 = st.columns(2)
            with col_w1:
                nouveau_ratio = st.slider(
                    "📐 Nouveau ratio mensualité / revenu",
                    min_value=0.0, max_value=1.0,
                    value=float(row['monthly_payment_ratio']),
                    step=0.01,
                    key="whatif_ratio"
                )
            with col_w2:
                nouveau_revenu = st.number_input(
                    "💰 Nouveau revenu annuel",
                    min_value=100_000, max_value=50_000_000,
                    value=int(row['annual_income']),
                    step=100_000,
                    key="whatif_revenu"
                )

            if st.button("🔄 Simuler le nouveau score", key="whatif_btn"):
                client_modifie = row.copy()
                client_modifie['monthly_payment_ratio'] = nouveau_ratio
                client_modifie['annual_income']         = nouveau_revenu

                df_modifie   = pd.DataFrame([client_modifie])
                X_modifie = preprocesser_et_aligner(df_modifie, X.columns)
                nouveau_score = predire_score(model, X_modifie, 0)

                diff          = nouveau_score - score
                pct_diff      = (diff / score) * 100
                categorie_sim, couleur_sim, decision_sim = categorie_du_score(nouveau_score)

                col_comp1, col_comp2 = st.columns(2)
                with col_comp1:
                    st.markdown(f"""
                    <div style="background:#f1f5f9; padding:18px; border-radius:12px; text-align:center;">
                        <div style="font-size:.7em; color:#64748b;">📌 Score actuel</div>
                        <div style="font-size:2.5em; font-weight:900; color:{couleur};">{score:.0f}</div>
                        <div style="font-weight:600; color:{couleur};">{categorie}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_comp2:
                    st.markdown(f"""
                    <div style="background:#f1f5f9; padding:18px; border-radius:12px; text-align:center;
                                border:2px solid {couleur_sim};">
                        <div style="font-size:.7em; color:#64748b;">🔮 Score simulé</div>
                        <div style="font-size:2.5em; font-weight:900; color:{couleur_sim};">{nouveau_score:.0f}</div>
                        <div style="font-weight:600; color:{couleur_sim};">{categorie_sim}</div>
                    </div>
                    """, unsafe_allow_html=True)

                arrow  = "📈 +" if diff > 0 else "📉 "
                bg_col = "#ecfdf5" if diff > 0 else "#fef2f2"
                bd_col = "#a7f3d0" if diff > 0 else "#fecaca"
                txt_col = "#10b981" if diff > 0 else "#ef4444"
                st.markdown(f"""
                <div style="margin-top:14px; padding:14px 18px; border-radius:12px;
                            background:{bg_col}; border:1px solid {bd_col};">
                    <b style="color:{txt_col};">{arrow}{diff:.1f} points ({pct_diff:+.1f}%)</b>
                    <span style="color:#64748b; margin-left:8px;">{decision_sim}</span>
                </div>
                """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────
    # ONGLET 3 — Analyse comparée
    # ────────────────────────────────────────────────────────
    with onglet3:

        st.markdown("### 📊 Comparaison avec le portefeuille")
        col_c1, col_c2, col_c3 = st.columns(3)

        with col_c1:
            st.markdown(f"""
            <div style="background:white; padding:18px; border-radius:12px;
                        border:1px solid #eef2f6; text-align:center;
                        box-shadow:0 2px 8px rgba(0,0,0,.04);">
                <div style="font-size:.7em; color:#64748b;">💳 Score du client</div>
                <div style="font-size:2.1em; font-weight:900; color:{couleur};">{score:.0f}</div>
                <div style="font-size:.75em; color:{couleur}; font-weight:600;">{categorie}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_c2:
            st.markdown(f"""
            <div style="background:white; padding:18px; border-radius:12px;
                        border:1px solid #eef2f6; text-align:center;
                        box-shadow:0 2px 8px rgba(0,0,0,.04);">
                <div style="font-size:.7em; color:#64748b;">🏦 Moyenne portefeuille</div>
                <div style="font-size:2.1em; font-weight:900; color:#1a5fa0;">{moyenne_portefeuille:.0f}</div>
                <div style="font-size:.75em; color:#64748b; font-weight:600;">Référence</div>
            </div>
            """, unsafe_allow_html=True)

        with col_c3:
            ecart_color = couleur if ecart_vs_moy > 0 else ACREMAC_COLORS["danger"]
            st.markdown(f"""
            <div style="background:white; padding:18px; border-radius:12px;
                        border:1px solid #eef2f6; text-align:center;
                        border-top:4px solid {ecart_color};
                        box-shadow:0 2px 8px rgba(0,0,0,.04);">
                <div style="font-size:.7em; color:#64748b;">{tendance_icone} Écart</div>
                <div style="font-size:2.1em; font-weight:900; color:{ecart_color};">{ecart_vs_moy:+.0f}</div>
                <div style="font-size:.75em; color:#64748b; font-weight:600;">{ecart_vs_moy/score*100:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # Indicateur visuel tendance
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px;
                    background:#f8fafc; padding:12px 18px; border-radius:10px;
                    border:1px solid #eef2f6; margin-top:20px;">
            <span style="font-size:1.5em;">{tendance_icone}</span>
            <span style="font-weight:600; color:#334155;">{tendance_texte}</span>
        </div>
        """, unsafe_allow_html=True)

















































# ============================================================
# PAGE : RAPPORT (VERSION ULTIME — ANIMÉ & INTERACTIF)
# ============================================================

elif page == "📄 Rapport":
    
    # ─── CSS ANIMATIONS & DESIGN ──────────────────────────────────────────
    st.markdown("""
    <style>
        /* ── Animations d'entrée ── */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(60px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.2); }
            50% { box-shadow: 0 0 40px rgba(16, 185, 129, 0.4); }
        }
        @keyframes shimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        @keyframes countUp {
            from { opacity: 0; transform: scale(0.5); }
            to { opacity: 1; transform: scale(1); }
        }
        @keyframes gradientMove {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .animate-fade { animation: fadeInUp 0.7s ease-out; }
        .animate-slide { animation: slideInRight 0.6s ease-out; }
        .animate-pulse-glow { animation: pulseGlow 2s infinite; }
        .animate-count { animation: countUp 0.8s cubic-bezier(0.22, 1, 0.36, 1); }
        
        /* ── Cartes Premium ── */
        .premium-card-ultime {
            background: white;
            border-radius: 20px;
            padding: 24px 28px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
            border: 1px solid rgba(0,0,0,0.04);
            transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
            height: 100%;
            position: relative;
            overflow: hidden;
        }
        .premium-card-ultime::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #0d1f3c, #1a5fa0, #D8A03F);
            background-size: 200% 100%;
            animation: gradientMove 3s ease infinite;
        }
        .premium-card-ultime:hover {
            transform: translateY(-6px);
            box-shadow: 0 16px 48px rgba(0,0,0,0.12);
        }
        
        /* ── Badges ── */
        .badge-ultime {
            display: inline-block;
            padding: 6px 18px;
            border-radius: 50px;
            font-size: 0.7em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 2px solid;
            transition: all 0.3s;
        }
        .badge-ultime:hover {
            transform: scale(1.05);
        }
        
        /* ── Shimmer Text ── */
        .shimmer-ultime {
            background: linear-gradient(90deg, #0d1f3c 25%, #1a5fa0 50%, #0d1f3c 75%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s infinite;
        }
        
        /* ── Header Premium ── */
        .header-ultime {
            background: linear-gradient(135deg, #0d1f3c 0%, #1a3a6b 40%, #1a5fa0 100%);
            padding: 28px 36px;
            border-radius: 20px;
            color: white;
            position: relative;
            overflow: hidden;
        }
        .header-ultime::before {
            content: '';
            position: absolute;
            top: -60%;
            right: -10%;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(232,97,26,0.12) 0%, transparent 70%);
            border-radius: 50%;
            animation: pulseGlow 4s infinite;
        }
        .header-ultime::after {
            content: '';
            position: absolute;
            bottom: -40%;
            left: -10%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(216,160,63,0.08) 0%, transparent 70%);
            border-radius: 50%;
        }
        
        /* ── Progress Bar Premium ── */
        .progress-premium {
            background: #f1f5f9;
            border-radius: 12px;
            height: 24px;
            overflow: hidden;
            position: relative;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.04);
        }
        .progress-premium .fill {
            height: 100%;
            border-radius: 12px;
            transition: width 1.5s cubic-bezier(0.22, 1, 0.36, 1);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 12px;
            font-size: 0.7em;
            font-weight: 700;
            color: white;
            min-width: 40px;
        }
        .progress-premium .fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
            background-size: 200% 100%;
            animation: shimmer 2s infinite;
        }
        
        /* ── Flag container ── */
        .flag-ultime {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 4px 16px 4px 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 50px;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(4px);
        }
        .flag-ultime span {
            font-size: 1.4em;
        }
        
        /* ── Conclusion line ── */
        .conclusion-line {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            padding: 14px 20px;
            background: #f8fafc;
            border-radius: 12px;
            font-size: 0.92em;
            color: #475569;
            line-height: 1.6;
        }
        .conclusion-line .badge {
            display: inline-block;
            padding: 2px 12px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 0.75em;
            white-space: nowrap;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ─── HEADER ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="header-ultime animate-fade">
        <div style="position:relative;z-index:1;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
            <div>
                <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                    <span style="font-size:2.8em;">🏦</span>
                    <div>
                        <div style="font-size:0.65em;text-transform:uppercase;letter-spacing:3px;color:rgba(255,255,255,0.4);">ACREMAC · Scoring IA</div>
                        <h1 style="color:white;margin:2px 0;font-size:2em;font-weight:900;letter-spacing:-0.5px;">📄 Rapport de Solvabilité</h1>
                        <p style="color:rgba(255,255,255,0.6);margin:0;font-size:0.85em;">Analyse approfondie du risque de crédit · Explicabilité SHAP</p>
                    </div>
                </div>
            </div>
            <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <span class="flag-ultime"><span>🔒</span> Sécurisé</span>
                <span class="flag-ultime"><span>🤖</span> IA explicable</span>
                <span class="flag-ultime"><span>⚡</span> Temps réel</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not CHARGEMENT_OK:
        st.error(f"❌ Erreur : {ERREUR}")
        st.stop()
    
    # ─── SÉLECTION ──────────────────────────────────────────────────────────
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        client_id = st.selectbox("Sélectionner un client", df_brut['client_id'].tolist(), key="report")
    with col_btn:
        st.write("")
        generer = st.button("🚀 Générer le rapport complet", use_container_width=True)
    
    if generer:
        import plotly.graph_objects as go
        import plotly.express as px
        import json
        
        idx = df_brut[df_brut['client_id'] == client_id].index[0]
        score = predire_score(model, X, idx)
        categorie, couleur, decision = categorie_du_score(score)
        row = df_brut.iloc[idx]
        shap_client = shap_df.iloc[idx]
        top_pos = shap_client.sort_values(ascending=False).head(8)
        top_neg = shap_client.sort_values(ascending=True).head(8)
        
        # ─── CALCULS ──────────────────────────────────────────────────────
        ratio_endettement = (row['loan_amount'] / row['annual_income'] * 100) if row['annual_income'] > 0 else 0
        ratio_mensualite = row['monthly_payment_ratio'] * 100
        score_pct = (score - 466) / (737 - 466) * 100
        anciennete_norm = min(row['credit_history_years'] / 20 * 100, 100)
        ratio_garantie = (row['collateral_value'] / row['loan_amount'] * 100) if row['loan_amount'] > 0 else 0
        
        # ─── DRAPEAUX OBLIGATOIRES ──────────────────────────────────────────
        pays_emoji = ""
        if row['country'] == 'Cameroun':
            pays_emoji = "🇨🇲"
        elif row['country'] == 'Congo':
            pays_emoji = "🇨🇬"
        elif row['country'] == 'Gabon':
            pays_emoji = "🇬🇦"
        elif row['country'] == 'Tchad':
            pays_emoji = "🇹🇩"
        else:
            pays_emoji = "🌍"
        
        if score >= 680:
            interpretation = "Client présentant une solvabilité très solide, avec une capacité de remboursement confortable et un historique de paiement irréprochable."
            recommandation = "Crédit recommandé dans des conditions standard. Des conditions préférentielles peuvent être envisagées."
            couleur_texte = "#10b981"
            niveau_risque = "Très Faible"
            icone_risque = "🟢"
        elif score >= 620:
            interpretation = "Client présentant une solvabilité satisfaisante. Le comportement de paiement est globalement bon."
            recommandation = "Crédit accordé avec des conditions standard. Une surveillance régulière est conseillée."
            couleur_texte = "#f59e0b"
            niveau_risque = "Faible"
            icone_risque = "🟡"
        elif score >= 560:
            interpretation = "Client présentant une solvabilité moyenne. Des signes de fragilité financière sont détectés."
            recommandation = "Crédit accordé sous conditions renforcées (garanties supplémentaires, suivi rapproché)."
            couleur_texte = "#f97316"
            niveau_risque = "Modéré"
            icone_risque = "🟠"
        else:
            interpretation = "Client présentant une solvabilité fragile. Des incidents de paiement significatifs sont enregistrés."
            recommandation = "Crédit à refuser ou à accorder avec des conditions très strictes."
            couleur_texte = "#ef4444"
            niveau_risque = "Élevé"
            icone_risque = "🔴"
        
        # ─── 1. EXECUTIVE SUMMARY ANIMÉ ───────────────────────────────────
        st.markdown('<div class="animate-fade">', unsafe_allow_html=True)
        st.markdown("### 📋 1. EXECUTIVE SUMMARY")
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            delta = {'reference': base_value, 'valueformat': '.0f', 'position': 'top'},
            title = {'text': "Score de solvabilité", 'font': {'size': 14, 'color': '#64748b'}},
            gauge = {
                'axis': {'range': [466, 737], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': couleur, 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "rgba(0,0,0,0.08)",
                'steps': [
                    {'range': [466, 560], 'color': 'rgba(239, 68, 68, 0.15)'},
                    {'range': [560, 620], 'color': 'rgba(249, 115, 22, 0.15)'},
                    {'range': [620, 680], 'color': 'rgba(245, 158, 11, 0.15)'},
                    {'range': [680, 737], 'color': 'rgba(16, 185, 129, 0.15)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 620
                }
            }
        ))
        fig_gauge.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1e293b')
        )
        
        col_g1, col_g2, col_g3, col_g4 = st.columns([1.5, 1, 1, 1])
        with col_g1:
            st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
        
        with col_g2:
            st.markdown(f"""
            <div class="premium-card-ultime animate-count" style="text-align:center;border-top-color:{couleur};">
                <div style="font-size:2.8em;font-weight:900;color:{couleur};">{score:.0f}</div>
                <div style="color:#64748b;font-size:0.7em;">Score</div>
                <div style="font-size:2em;margin-top:8px;">{pays_emoji}</div>
                <div style="font-size:0.7em;color:#94a3b8;">{row['country']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_g3:
            st.markdown(f"""
            <div class="premium-card-ultime animate-count" style="text-align:center;border-top-color:{couleur};">
                <div style="font-size:1.6em;font-weight:800;color:{couleur};">{categorie}</div>
                <div style="color:#64748b;font-size:0.7em;">Catégorie</div>
                <div style="font-size:1.2em;margin-top:8px;">{icone_risque}</div>
                <div style="font-size:0.7em;color:#94a3b8;">Risque {niveau_risque}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_g4:
            st.markdown(f"""
            <div class="premium-card-ultime animate-count" style="text-align:center;border-top-color:{couleur};">
                <div style="font-size:1em;font-weight:700;color:#0d1f3c;">{decision}</div>
                <div style="color:#64748b;font-size:0.7em;">Décision</div>
                <div style="font-size:1.2em;margin-top:8px;">💳</div>
                <div style="font-size:0.7em;color:#94a3b8;">Confiance élevée</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── 2. RADAR CHART (Profil de risque) ────────────────────────────
        st.markdown("### 🎯 2. PROFIL DE RISQUE INTERACTIF")
        
        col_radar, col_radar_info = st.columns([2, 1])
        
        with col_radar:
            categories = ['Solvabilité', 'Historique', 'Comportement', 'Capacité', 'Garantie', 'Stabilité']
            
            val_solvabilite = min(score / 737 * 100, 100)
            val_historique = 100 - min(row['past_defaults'] / 3 * 100, 100)
            val_comportement = 100 - min(row['days_late_avg'] / 120 * 100, 100)
            val_capacite = 100 - min(ratio_mensualite / 80 * 100, 100)
            val_garantie = min(ratio_garantie / 100 * 100, 100)
            val_stabilite = min(anciennete_norm, 100)
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=[val_solvabilite, val_historique, val_comportement, val_capacite, val_garantie, val_stabilite],
                theta=categories,
                fill='toself',
                name='Profil client',
                line_color=couleur,
                fillcolor=couleur,
                opacity=0.6,
                hovertemplate='%{theta}: %{r:.0f}%<extra></extra>'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=[70, 70, 70, 70, 70, 70],
                theta=categories,
                fill='toself',
                name='Référence',
                line_color='#94a3b8',
                fillcolor='rgba(148, 163, 184, 0.2)',
                opacity=0.3,
                hovertemplate='Référence: %{r:.0f}%<extra></extra>'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont_size=9),
                    angularaxis=dict(tickfont_size=10, rotation=90)
                ),
                height=380,
                margin=dict(l=40, r=40, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1e293b'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15)
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        
        with col_radar_info:
            st.markdown(f"""
            <div class="premium-card-ultime animate-slide" style="border-top-color:{couleur};">
                <b style="color:#0d1f3c;">📌 Synthèse du profil</b>
                <div style="font-size:0.85em;color:#475569;margin-top:8px;line-height:1.8;">
                    <div><b>Score :</b> <span style="color:{couleur};font-weight:800;">{score:.0f}/737</span></div>
                    <div><b>Catégorie :</b> <span style="color:{couleur};font-weight:700;">{categorie}</span></div>
                    <div><b>Risque :</b> {icone_risque} {niveau_risque}</div>
                    <div><b>Décision :</b> {decision}</div>
                    <div style="margin-top:8px;"><b>Niveaux atteints :</b></div>
                    <div style="margin-left:12px;font-size:0.8em;">
                        <div>🟢 Solvabilité : {val_solvabilite:.0f}%</div>
                        <div>🟢 Historique : {val_historique:.0f}%</div>
                        <div>🟡 Comportement : {val_comportement:.0f}%</div>
                        <div>🟡 Capacité : {val_capacite:.0f}%</div>
                        <div>🔵 Garantie : {val_garantie:.0f}%</div>
                        <div>🔵 Stabilité : {val_stabilite:.0f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ─── 3. ANALYSE DES CONTRIBUTIONS SHAP ───────────────────────────
        st.markdown("### 🔍 3. ANALYSE DES CONTRIBUTIONS SHAP")
        
        col_shap_pos, col_shap_neg = st.columns(2)
        
        with col_shap_pos:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#ecfdf5,#d1fae5);padding:12px 16px;border-radius:12px;border-left:4px solid #10b981;margin-bottom:12px;">
                <b style="color:#059669;">✅ Facteurs favorables</b>
                <span style="float:right;font-size:0.7em;color:#059669;">Augmentent le score</span>
            </div>
            """, unsafe_allow_html=True)
            for var, val in top_pos.head(6).items():
                pct_impact = abs(val) / shap_client.abs().sum() * 100
                bar_width = min(pct_impact * 10, 100)
                st.markdown(f"""
                <div style="background:#f0fdf4;padding:10px 14px;border-radius:10px;margin:6px 0;border-left:3px solid #10b981;transition:all 0.3s;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.85em;font-weight:500;">{var}</span>
                        <span style="font-weight:700;color:#059669;">+{val:.2f} pts</span>
                    </div>
                    <div class="progress-premium" style="height:6px;margin-top:4px;">
                        <div class="fill" style="width:{bar_width}%;background:linear-gradient(90deg,#10b981,#34d399);height:6px;min-width:0;padding:0;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_shap_neg:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#fef2f2,#fecaca);padding:12px 16px;border-radius:12px;border-left:4px solid #ef4444;margin-bottom:12px;">
                <b style="color:#dc2626;">⚠️ Facteurs défavorables</b>
                <span style="float:right;font-size:0.7em;color:#dc2626;">Diminuent le score</span>
            </div>
            """, unsafe_allow_html=True)
            for var, val in top_neg.head(6).items():
                pct_impact = abs(val) / shap_client.abs().sum() * 100
                bar_width = min(pct_impact * 10, 100)
                st.markdown(f"""
                <div style="background:#fef2f2;padding:10px 14px;border-radius:10px;margin:6px 0;border-left:3px solid #ef4444;transition:all 0.3s;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.85em;font-weight:500;">{var}</span>
                        <span style="font-weight:700;color:#dc2626;">{val:.2f} pts</span>
                    </div>
                    <div class="progress-premium" style="height:6px;margin-top:4px;">
                        <div class="fill" style="width:{bar_width}%;background:linear-gradient(90deg,#ef4444,#f87171);height:6px;min-width:0;padding:0;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # ─── 4. WATERFALL INTERACTIF ──────────────────────────────────────
        st.markdown("### 📈 4. DÉCOMPOSITION SHAP INTERACTIVE")
        
        shap_sorted_plot = shap_client.sort_values()
        colors_plot = ['#ef4444' if v < 0 else '#10b981' for v in shap_sorted_plot.values]
        
        fig_waterfall_interactive = go.Figure()
        
        fig_waterfall_interactive.add_trace(go.Bar(
            y=shap_sorted_plot.index,
            x=shap_sorted_plot.values,
            orientation='h',
            marker_color=colors_plot,
            text=[f'{v:+.2f}' for v in shap_sorted_plot.values],
            textposition='outside',
            textfont=dict(size=10, color='#1e293b'),
            hovertemplate='<b>%{y}</b><br>Contribution: %{x:+.2f} pts<extra></extra>',
            name='Contributions SHAP'
        ))
        
        fig_waterfall_interactive.add_vline(x=0, line_dash="dash", line_color="#64748b", opacity=0.5)
        
        fig_waterfall_interactive.update_layout(
            title=dict(
                text=f'Score: {score:.0f} pts · Référence: {base_value:.0f} pts · {categorie}',
                font=dict(size=14, color='#1e293b', weight='bold')
            ),
            xaxis_title='Contribution (points)',
            yaxis_title='Variable',
            height=450,
            margin=dict(l=10, r=80, t=60, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1e293b'),
            showlegend=False,
            xaxis=dict(gridcolor='rgba(0,0,0,0.05)', zeroline=False),
            yaxis=dict(gridcolor='rgba(0,0,0,0.05)')
        )
        
        st.plotly_chart(fig_waterfall_interactive, use_container_width=True, config={'displayModeBar': True})
        
        # ─── 5. IDENTIFICATION ─────────────────────────────────────────────
        st.markdown("### 👤 5. IDENTIFICATION DU CLIENT")
        
        col_id1, col_id2, col_id3 = st.columns(3)
        with col_id1:
            st.markdown(f"""
            <div class="premium-card-ultime animate-fade">
                <b style="color:#0d1f3c;">📌 Identité</b>
                <div style="display:flex;align-items:center;gap:12px;margin-top:8px;">
                    <span style="font-size:2.5em;">👤</span>
                    <div>
                        <div style="font-weight:800;color:#0d1f3c;font-size:1.1em;">{client_id}</div>
                        <div style="font-size:0.8em;color:#64748b;">{row['client_type']} · {int(row['age'])} ans</div>
                    </div>
                </div>
                <div class="progress-premium" style="height:4px;margin-top:8px;">
                    <div class="fill" style="width:100%;background:linear-gradient(90deg,#0d1f3c,#1a5fa0);height:4px;min-width:0;padding:0;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_id2:
            st.markdown(f"""
            <div class="premium-card-ultime animate-fade">
                <b style="color:#0d1f3c;">📍 Localisation</b>
                <div style="display:flex;align-items:center;gap:12px;margin-top:8px;">
                    <span style="font-size:2.5em;">{pays_emoji}</span>
                    <div>
                        <div style="font-weight:800;color:#0d1f3c;font-size:1.1em;">{row['country']}</div>
                        <div style="font-size:0.8em;color:#64748b;">{row['sector']}</div>
                    </div>
                </div>
                <div style="font-size:0.8em;color:#64748b;margin-top:4px;">Ancienneté: {int(row['credit_history_years'])} ans</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_id3:
            st.markdown(f"""
            <div class="premium-card-ultime animate-fade">
                <b style="color:#0d1f3c;">💰 Situation financière</b>
                <div style="display:flex;justify-content:space-between;margin-top:8px;flex-wrap:wrap;">
                    <div><span style="font-size:0.7em;color:#64748b;">Revenu</span><br><b>{row['annual_income']:,.0f}</b></div>
                    <div><span style="font-size:0.7em;color:#64748b;">Crédit</span><br><b>{row['loan_amount']:,.0f}</b></div>
                    <div><span style="font-size:0.7em;color:#64748b;">Durée</span><br><b>{int(row['loan_duration_months'])} mois</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ─── 6. TABLEAU DE BORD FINANCIER ─────────────────────────────────
        st.markdown("### 📊 6. TABLEAU DE BORD FINANCIER")
        
        col_rat1, col_rat2, col_rat3, col_rat4 = st.columns(4)
        
        def create_gauge(value, max_val, color, label, unit="%"):
            pct = min(value / max_val * 100, 100)
            return f"""
            <div class="premium-card-ultime" style="text-align:center;border-top-color:{color};">
                <div style="font-size:1.8em;font-weight:900;color:{color};">{value:.1f}{unit}</div>
                <div style="color:#64748b;font-size:0.7em;">{label}</div>
                <div class="progress-premium" style="height:6px;margin-top:6px;">
                    <div class="fill" style="width:{pct}%;background:{color};height:6px;min-width:0;padding:0;"></div>
                </div>
                <div style="font-size:0.6em;color:#94a3b8;margin-top:2px;">Seuil: {max_val}{unit}</div>
            </div>
            """
        
        with col_rat1:
            st.markdown(create_gauge(ratio_endettement, 60, '#10b981' if ratio_endettement < 30 else '#f97316' if ratio_endettement < 50 else '#ef4444', 'Endettement'), unsafe_allow_html=True)
        with col_rat2:
            st.markdown(create_gauge(ratio_mensualite, 80, '#10b981' if ratio_mensualite < 30 else '#f97316' if ratio_mensualite < 50 else '#ef4444', 'Mensualité/Revenu'), unsafe_allow_html=True)
        with col_rat3:
            st.markdown(create_gauge(anciennete_norm, 100, '#1a5fa0', 'Ancienneté crédit', '%'), unsafe_allow_html=True)
        with col_rat4:
            st.markdown(create_gauge(ratio_garantie, 100, '#8b5cf6', 'Couverture garantie', '%'), unsafe_allow_html=True)
        
        # ─── 7. CONCLUSION EN UNE LIGNE ────────────────────────────────────
        st.markdown("### 📝 7. CONCLUSION"); comportement_texte = comportement_texte if 'comportement_texte' in locals() else ""; endettement_texte = endettement_texte if 'endettement_texte' in locals() else ""; conclusion_one_line = f"Le client {client_id} ({row['sector']}, {row['country']} {pays_emoji}) présente un score de {score:.0f}/737, catégorie {categorie}. {comportement_texte} {endettement_texte}"; st.markdown(f'<div class="animate-fade" style="background:white;padding:20px 24px;border-radius:16px;border-left:6px solid {couleur};box-shadow:0 4px 20px rgba(0,0,0,0.06);"><div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;"><div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;"><span style="font-weight:700;color:#0d1f3c;font-size:1.1em;">📌 Conclusion</span><span class="badge-ultime" style="color:{couleur};border-color:{couleur};background:{couleur}15;font-size:0.65em;">{categorie}</span><span style="font-size:0.8em;color:#94a3b8;">|</span><span style="font-size:0.8em;color:#64748b;">Score: {score:.0f}/737</span></div><div style="display:flex;align-items:center;gap:8px;"><span style="font-size:0.75em;color:#64748b;">Décision:</span><span style="font-weight:700;color:{couleur};font-size:0.85em;">{decision}</span><span style="font-size:1.2em;">{icone_risque}</span></div></div><div style="margin-top:10px;padding:12px 16px;background:#f8fafc;border-radius:10px;border:1px solid #f1f5f9;"><p style="margin:0;color:#475569;font-size:0.95em;line-height:1.7;">{conclusion_one_line}</p></div><div style="display:flex;justify-content:flex-end;align-items:center;gap:12px;margin-top:10px;flex-wrap:wrap;"><span style="font-size:0.65em;color:#94a3b8;">🔍 SHAP TreeSHAP</span><span style="font-size:0.65em;color:#94a3b8;">|</span><span style="font-size:0.65em;color:#94a3b8;">Gradient Boosting</span><span style="font-size:0.65em;color:#94a3b8;">|</span><span style="font-size:0.65em;color:#94a3b8;">{pd.Timestamp.now().strftime("%d/%m/%Y")}</span></div></div>', unsafe_allow_html=True)
        # ─── 8. EXPORT ──────────────────────────────────────────────────────
        st.markdown("### 📥 8. EXPORT DU RAPPORT")
        
        st.markdown("""
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin:12px 0;">
            <span style="background:#f1f5f9;padding:4px 14px;border-radius:20px;font-size:0.7em;color:#64748b;">📝 TXT</span>
            <span style="background:#f1f5f9;padding:4px 14px;border-radius:20px;font-size:0.7em;color:#64748b;">🔷 JSON</span>
            <span style="background:#f1f5f9;padding:4px 14px;border-radius:20px;font-size:0.7em;color:#64748b;">🌐 HTML</span>
            <span style="background:#f1f5f9;padding:4px 14px;border-radius:20px;font-size:0.7em;color:#64748b;">📄 PDF</span>
        </div>
        """, unsafe_allow_html=True)
        
        col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
        
        # TXT
        rapport_txt = f"""RAPPORT DE SOLVABILITÉ — ACREMAC
================================

IDENTIFICATION
--------------
Client          : {client_id}
Type            : {row['client_type']}
Âge             : {int(row['age'])} ans
Pays            : {row['country']} {pays_emoji}
Secteur         : {row['sector']}

SCORE ET DÉCISION
-----------------
Score           : {score:.0f} / 737
Catégorie       : {categorie}
Décision        : {decision}
Risque          : {niveau_risque}

ANALYSE FINANCIÈRE
------------------
Revenu annuel   : {row['annual_income']:,.0f}
Crédit demandé  : {row['loan_amount']:,.0f}
Durée crédit    : {int(row['loan_duration_months'])} mois
Taux d'intérêt  : {row['interest_rate']:.2f}%

COMPORTEMENT DE PAIEMENT
------------------------
Défauts passés  : {int(row['past_defaults'])}
Retard moyen    : {row['days_late_avg']:.1f} jours
Ratio mensualité: {row['monthly_payment_ratio']:.3f}

RATIOS CLÉS
-----------
Endettement     : {ratio_endettement:.1f}%
Mensualité/Revenu: {ratio_mensualite:.1f}%

FACTEURS FAVORABLES
-------------------
{chr(10).join([f"{k} : +{v:.2f} pts" for k,v in top_pos.head(5).items()])}

FACTEURS DÉFAVORABLES
---------------------
{chr(10).join([f"{k} : {v:.2f} pts" for k,v in top_neg.head(5).items()])}

CONCLUSION
----------
{conclusion_one_line}

────────────────────────────────────────────────────────────
Généré par le Moteur IA ACREMAC · SHAP TreeSHAP
{client_id} · {pd.Timestamp.now().strftime('%d/%m/%Y')}
"""
        
        with col_exp1:
            st.download_button("📝 TXT", rapport_txt, file_name=f"rapport_{client_id}.txt", mime="text/plain", use_container_width=True)
        
        # JSON
        with col_exp2:
            rapport_json = {
                "client_id": client_id, "score": round(score, 2), "categorie": categorie, "decision": decision,
                "profil": {"type": row['client_type'], "age": int(row['age']), "pays": row['country'], "secteur": row['sector']},
                "ratios": {"endettement": round(ratio_endettement, 1), "mensualite_revenu": round(ratio_mensualite, 1)},
                "shap": {"top_positif": {k: round(float(v), 2) for k, v in top_pos.head(5).items()},
                         "top_negatif": {k: round(float(v), 2) for k, v in top_neg.head(5).items()}},
                "conclusion": conclusion_one_line
            }
            st.download_button("🔷 JSON", json.dumps(rapport_json, ensure_ascii=False, indent=2), file_name=f"rapport_{client_id}.json", mime="application/json", use_container_width=True)
        
        # HTML
        with col_exp3:
            html_content = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><title>Rapport {client_id}</title>
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#f0f4f8;padding:40px;color:#1e293b;}}
.header{{background:linear-gradient(135deg,#0d1f3c,#1a5fa0);color:white;border-radius:16px;padding:30px;max-width:900px;margin:0 auto 20px;}}
.card{{background:white;border-radius:12px;padding:20px 24px;max-width:900px;margin:0 auto 16px;box-shadow:0 2px 12px rgba(0,0,0,0.06);}}
.score{{font-size:3.5em;font-weight:900;color:{couleur};}}
.badge{{display:inline-block;padding:4px 16px;border-radius:50px;font-weight:700;background:{couleur}20;border:2px solid {couleur};color:{couleur};}}
table{{width:100%;border-collapse:collapse;font-size:0.9em;}}
td{{padding:6px 4px;border-bottom:1px solid #f1f5f9;}}
td:first-child{{color:#64748b;width:50%;}}
.factor-pos{{background:#ecfdf5;padding:4px 10px;border-radius:4px;margin:2px 0;border-left:3px solid #10b981;display:flex;justify-content:space-between;}}
.factor-neg{{background:#fef2f2;padding:4px 10px;border-radius:4px;margin:2px 0;border-left:3px solid #ef4444;display:flex;justify-content:space-between;}}
.progress{{background:#f1f5f9;border-radius:6px;height:6px;overflow:hidden;margin:4px 0;}}
.progress-fill{{height:100%;border-radius:6px;transition:width 1s;}}
</style></head>
<body>
<div class="header"><h2 style="margin:0;">🏦 ACREMAC — Rapport de Solvabilité</h2>
<p style="color:rgba(255,255,255,0.7);margin:4px 0 0;">{client_id} · {row['country']} {pays_emoji} · {pd.Timestamp.now().strftime('%d/%m/%Y')}</p></div>
<div class="card" style="text-align:center;">
<div class="score">{score:.0f}</div>
<div style="color:#64748b;">/ 737 pts</div>
<div class="badge">{categorie}</div>
<div style="margin-top:8px;font-weight:600;">{decision}</div>
<div class="progress"><div class="progress-fill" style="width:{score_pct:.1f}%;background:{couleur};"></div></div>
</div>
<div class="card"><h3>📋 Profil client</h3>
<table><tr><td>ID Client</td><td><b>{client_id}</b></td></tr>
<tr><td>Type</td><td>{row['client_type']}</td></tr>
<tr><td>Âge</td><td>{int(row['age'])} ans</td></tr>
<tr><td>Pays</td><td>{row['country']} {pays_emoji}</td></tr>
<tr><td>Secteur</td><td>{row['sector']}</td></tr>
<tr><td>Revenu annuel</td><td>{row['annual_income']:,.0f}</td></tr>
</table></div>
<div class="card"><h3>✅ Facteurs favorables</h3>
{''.join([f"<div class='factor-pos'><span>{k}</span><span style='color:#059669;font-weight:600;'>+{v:.2f} pts</span></div>" for k,v in top_pos.head(5).items()])}
<h3 style="margin-top:12px;">⚠️ Facteurs défavorables</h3>
{''.join([f"<div class='factor-neg'><span>{k}</span><span style='color:#dc2626;font-weight:600;'>{v:.2f} pts</span></div>" for k,v in top_neg.head(5).items()])}
</div>
<div class="card"><h3>📝 Conclusion</h3>
<p style="color:#475569;font-size:0.9em;line-height:1.6;">{conclusion_one_line}</p></div>
<p style="text-align:center;color:#94a3b8;font-size:0.7em;">Généré par ACREMAC · SHAP TreeSHAP</p>
</body></html>"""
            st.download_button("🌐 HTML", html_content, file_name=f"rapport_{client_id}.html", mime="text/html", use_container_width=True)
        
        with col_exp4:
            st.download_button("📄 PDF", pdf_bytes, file_name=f"rapport_{client_id}.pdf", mime="application/pdf", use_container_width=True)
        
        st.success("✅ Rapport premium généré avec succès !")
st.divider()
st.caption("🏦 ACREMAC — Moteur de Scoring de Solvabilité | PFE 2025-2026 | Diono dit Boubacar PEROU")