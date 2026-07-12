"""
shap_explainer.py — Couche Explicabilité (SHAP)
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from model import predire_score, charger_shap

@st.cache_data
def get_shap_data():
    """Récupère les données SHAP"""
    shap_df, config = charger_shap()
    base_value = float(config['base_value'])
    return shap_df, base_value

def categorie_du_score(score):
    """Catégorisation du score"""
    if score >= 680:
        return "Excellent", "#10b981", "✅ Crédit recommandé"
    elif score >= 620:
        return "Bon", "#f59e0b", "✅ Conditions standard"
    elif score >= 560:
        return "Moyen", "#f97316", "⚠️ Garanties renforcées"
    else:
        return "Risqué", "#ef4444", "🚫 Crédit refusé"

def afficher_waterfall(idx, model, X, shap_df, base_value):
    """Affiche un waterfall plot SHAP pour un client"""
    shap_client = shap_df.iloc[idx]
    top_10 = shap_client.abs().sort_values(ascending=False).head(10)
    shap_sorted = shap_client[top_10.index].sort_values()
    
    score = predire_score(model, X, idx)
    categorie, couleur, _ = categorie_du_score(score)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#fafbfc')
    
    colors = ['#ef4444' if v < 0 else '#10b981' for v in shap_sorted.values]
    bars = ax.barh(range(len(shap_sorted)), shap_sorted.values, color=colors, height=0.6, edgecolor='white', linewidth=1.5)
    
    ax.set_yticks(range(len(shap_sorted)))
    ax.set_yticklabels(shap_sorted.index, fontsize=10)
    ax.axvline(0, color='#e2e8f0', linewidth=1.5)
    
    for bar, val in zip(bars, shap_sorted.values):
        offset = max(0.3, abs(val) * 0.04)
        ax.text(val + (offset if val >= 0 else -offset),
                bar.get_y() + bar.get_height()/2,
                f'{val:+.1f}', va='center',
                ha='left' if val >= 0 else 'right',
                fontsize=9, fontweight='bold',
                color='#059669' if val >= 0 else '#dc2626')
    
    pos_patch = mpatches.Patch(color='#10b981', alpha=0.9, label='Facteur favorable')
    neg_patch = mpatches.Patch(color='#ef4444', alpha=0.9, label='Facteur défavorable')
    ax.legend(handles=[pos_patch, neg_patch], fontsize=9, loc='lower right', framealpha=0.95)
    
    ax.set_title(f'Score: {score:.0f} pts · {categorie} · Référence: {base_value:.0f} pts', 
                 fontsize=12, fontweight='700')
    ax.set_xlabel('Contribution (points)', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#e2e8f0')
    ax.grid(axis='x', alpha=0.4, linestyle='--', color='#e2e8f0')
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()