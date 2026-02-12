import streamlit as st
import pandas as pd
import json, io, re

# --- CONFIGURATION DE L'APP ---
st.set_page_config(page_title="Menzberg Live Logistics", layout="wide", page_icon="⚡")

# Initialisation de la mémoire de l'app (stocke les commandes reçues)
if 'commandes_live' not in st.session_state:
    st.session_state['commandes_live'] = []

# --- DESIGN MENZBERG ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1 { color: #007bff; border-bottom: 3px solid #FFD700; padding-bottom: 10px; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Menzberg Live : Tableau de Bord Atelier")

# --- LE CERVEAU LOGIQUE (Menzberg Engine) ---
def traiter_donnees_tiktak(data):
    """ Transforme le JSON reçu de TikTak en lignes de production """
    lignes_production = []
    nom_client = data.get('name', 'Client Inconnu')
    ville = data.get('gouvernorat', '-')
    
    for item in data.get('details', []):
        p_name = item.get('product_name', '')
        qte_cmd = int(item.get('quantity', 1))
        options = item.get('product_options', 'Non spécifiée')
        
        p_low = p_name.lower()
        
        # 1. LOGIQUE PACK 7 SACS
        if "pack 7" in p_low:
            lignes_production.append({
                "Client": nom_client, "Ville": ville, 
                "Produit": "Sac Standard", "Couleur": options, "Quantité": qte_cmd * 3
            })
            lignes_production.append({
                "Client": nom_client, "Ville": ville, 
                "Produit": "Sac BigBag", "Couleur": options, "Quantité": qte_cmd * 4
            })
        
        # 2. LOGIQUE PACK 5 SACS
        elif "pack 5" in p_low:
            lignes_production.append({
                "Client": nom_client, "Ville": ville, 
                "Produit": "Sac Standard", "Couleur": options, "Quantité": qte_cmd * 5
            })
            
        # 3. LOGIQUE BOUDINS DE PORTE
        elif any(x in p_low for x in ["boudin", "top tip", "anti-cafard"]):
            # Détection taille
            taille = "6-8 cm"
            if "3-4" in p_low or "3-4" in options: taille = "3-4 cm"
            elif "4-5" in p_low or "4-5" in options: taille = "4-5 cm"
            
            lignes_production.append({
                "Client": nom_client, "Ville": ville, 
                "Produit": f"Boudin {taille}", "Couleur": options, "Quantité": qte_cmd * 4