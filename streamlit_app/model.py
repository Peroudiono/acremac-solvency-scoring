"""
model.py — Couche Traitement et Modélisation
"""

import pickle
import json
import os
import streamlit as st
import pandas as pd
import numpy as np

@st.cache_resource
def charger_modele():
    """Charge le modèle Gradient Boosting et le scaler"""
    base = os.path.dirname(os.path.abspath(__file__))
    
    with open(os.path.join(base, '..', 'models', 'model_gradient_boosting.pkl'), 'rb') as f:
        model = pickle.load(f)
    
    return model

@st.cache_resource
def charger_shap():
    """Charge les données SHAP"""
    base = os.path.dirname(os.path.abspath(__file__))
    
    shap_df = pd.read_csv(os.path.join(base, '..', 'shap_results', 'shap_values_df.csv'))
    
    with open(os.path.join(base, '..', 'shap_results', 'shap_config.json'), 'r') as f:
        config = json.load(f)
    
    return shap_df, config

def preprocesser_pour_modele(df_brut):
    """Prétraitement des données (identique à Phase 2)"""
    df = df_brut.copy()
    df = df.drop(columns=['client_id'])
    df['client_type'] = (df['client_type'] == 'Personne_physique').astype(int)
    df = pd.get_dummies(df, columns=['sector', 'country'], drop_first=True)
    X = df.drop(columns=['solvency_score'])
    return X

def predire_score(model, X, idx):
    """Prédiction du score de solvabilité"""
    return float(model.predict(X.iloc[[idx]])[0])