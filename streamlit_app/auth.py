"""
auth.py — Gestion de l'authentification
Design identique à la maquette HTML fournie
"""

import streamlit as st
import hashlib
import os
import base64

# ─── BASE DE DONNÉES DES UTILISATEURS ────────────────────────────────────────
UTILISATEURS = {
    "admin": {
        "mot_de_passe_hache": hashlib.sha256("acremac2025".encode()).hexdigest(),
        "nom": "Administrateur",
        "role": "admin"
    },
    "analyste": {
        "mot_de_passe_hache": hashlib.sha256("analyste123".encode()).hexdigest(),
        "nom": "Analyste ACREMAC",
        "role": "analyste"
    },
    "boubacar": {
        "mot_de_passe_hache": hashlib.sha256("perou2025".encode()).hexdigest(),
        "nom": "Diono dit Boubacar PEROU",
        "role": "createur"
    }
}

# ─── CHEMINS DES IMAGES ────────────────────────────────────────────────────────
# Chemin absolu pour être sûr que ça fonctionne
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG_IMAGE = os.path.join(BASE_DIR, "images", "arriere.png")


def get_image_base64(path):
    """Convertit une image locale en chaîne Base64 pour l'inclusion HTML/CSS"""
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return ""


def verifier_authentification():
    """Vérifie si l'utilisateur est authentifié"""
    
    if st.session_state.get("authentifie", False):
        return True
    
    # Récupération de l'image de fond
    bg_base64 = get_image_base64(BG_IMAGE)
    
    # Injection CSS identique à la maquette HTML
    st.markdown(f"""
    <style>
        /* ── Reset et fond ── */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', sans-serif;
        }}
        
        .stApp {{
            height: 100vh !important;
            background-image: url("{bg_base64}") !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-size: contain !important;
            background-color: white !important;
            position: relative !important;
            overflow: hidden !important;
        }}
        
        /* ── Suppression des éléments Streamlit par défaut ── */
        #MainMenu, footer, header, [data-testid="stSidebar"], [data-testid="stHeader"] {{
            display: none !important;
        }}
        
        /* ── Boîte de connexion ── */
        .login-box {{
            position: absolute;
            top: 320px;
            right: 80px;
            width: 340px;
            padding: 25px;
            background: rgba(255, 255, 255, 0.92);
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
            z-index: 999;
        }}
        
        .login-box h1 {{
            color: #0F2D6B;
            font-size: 24px;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .login-box p {{
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        
        .input-group {{
            margin-bottom: 20px;
        }}
        
        .input-group label {{
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #222;
            font-size: 14px;
        }}
        
        .input-group input {{
            width: 100%;
            padding: 14px;
            border: 1px solid #d9d9d9;
            border-radius: 10px;
            outline: none;
            font-size: 14px;
        }}
        
        .input-group input:focus {{
            border-color: #D8A03F;
        }}
        
        .options {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            font-size: 14px;
        }}
        
        .options a {{
            text-decoration: none;
            color: #0F2D6B;
            font-size: 14px;
        }}
        
        .options a:hover {{
            text-decoration: underline;
        }}
        
        /* ── Bouton de connexion ── */
        .btn-login {{
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            color: white;
            cursor: pointer;
            background: linear-gradient(90deg, #173A7A, #D8A03F);
            transition: opacity 0.3s;
        }}
        
        .btn-login:hover {{
            opacity: 0.9;
        }}
        
        /* ── Pied de page ── */
        .footer {{
            text-align: center;
            margin-top: 25px;
            color: #888;
            font-size: 13px;
        }}
        
        /* ── Override Streamlit ── */
        div[data-testid="stForm"] {{
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
        }}
        
        .stTextInput > div {{
            margin-bottom: 0 !important;
        }}
        
        .stTextInput input {{
            width: 100% !important;
            padding: 14px !important;
            border: 1px solid #d9d9d9 !important;
            border-radius: 10px !important;
            outline: none !important;
            background: white !important;
            font-size: 14px !important;
            margin-bottom: 0 !important;
        }}
        
        .stTextInput input:focus {{
            border-color: #D8A03F !important;
            box-shadow: none !important;
        }}
        
        /* ── Checkbox ── */
        .stCheckbox {{
            display: flex;
            align-items: center;
        }}
        .stCheckbox label {{
            font-weight: 400 !important;
            color: #333 !important;
            font-size: 14px !important;
        }}
        
        /* ── Message d'erreur ── */
        .stAlert {{
            border-radius: 10px !important;
            font-size: 14px !important;
            margin-bottom: 15px !important;
        }}
        
        /* ── Lien "Mot de passe oublié" ── */
        .forgot-link {{
            color: #0F2D6B;
            text-decoration: none;
            font-size: 14px;
            cursor: pointer;
        }}
        .forgot-link:hover {{
            text-decoration: underline;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # ─── STRUCTURE HTML DE LA PAGE DE CONNEXION ──────────────────────────────
    st.markdown("""
    <div class="login-box">
        <h1>Connexion</h1>
        <p>Moteur IA de Scoring de Solvabilité</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ─── FORMULAIRE ──────────────────────────────────────────────────────────────
    with st.form("login_form"):
        st.markdown("""
        <div class="input-group">
            <label>Nom d'utilisateur</label>
        </div>
        """, unsafe_allow_html=True)
        
        nom_utilisateur = st.text_input("", placeholder="Entrer votre identifiant", label_visibility="collapsed")
        
        st.markdown("""
        <div class="input-group">
            <label>Mot de passe</label>
        </div>
        """, unsafe_allow_html=True)
        
        mot_de_passe = st.text_input("", type="password", placeholder="Entrer votre mot de passe", label_visibility="collapsed")
        
        # Options
        col_check, col_forgot = st.columns([1, 1])
        with col_check:
            st.checkbox("Se souvenir de moi")
        with col_forgot:
            st.markdown('<a href="#" class="forgot-link">Mot de passe oublié ?</a>', unsafe_allow_html=True)
        
        # Bouton de connexion
        submitted = st.form_submit_button("Se connecter")
        
        if submitted:
            if not nom_utilisateur or not mot_de_passe:
                st.error("❌ Veuillez remplir tous les champs")
            elif nom_utilisateur in UTILISATEURS:
                mot_de_passe_hache = hashlib.sha256(mot_de_passe.encode()).hexdigest()
                if mot_de_passe_hache == UTILISATEURS[nom_utilisateur]["mot_de_passe_hache"]:
                    st.session_state["authentifie"] = True
                    st.session_state["utilisateur"] = nom_utilisateur
                    st.session_state["nom_utilisateur"] = UTILISATEURS[nom_utilisateur]["nom"]
                    st.session_state["role"] = UTILISATEURS[nom_utilisateur]["role"]
                    st.rerun()
                else:
                    st.error("❌ Mot de passe incorrect")
            else:
                st.error("❌ Nom d'utilisateur inconnu")
    
    # ─── PIED DE PAGE ────────────────────────────────────────────────────────────
    st.markdown("""
        <div class="footer">
            © 2026 ACREMAC | HESTIM
        </div>
    """, unsafe_allow_html=True)
    
    return False


def deconnecter():
    """Déconnecte l'utilisateur"""
    for key in ["authentifie", "utilisateur", "nom_utilisateur", "role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def get_utilisateur_courant():
    """Retourne les informations de l'utilisateur connecté"""
    if st.session_state.get("authentifie", False):
        return {
            "login": st.session_state.get("utilisateur", ""),
            "nom": st.session_state.get("nom_utilisateur", ""),
            "role": st.session_state.get("role", "")
        }
    return None