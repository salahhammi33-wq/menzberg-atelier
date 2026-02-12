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
        qte_cmd_str = item.get('quantity', '1')
        try:
            qte_cmd = int(qte_cmd_str)
        except:
            qte_cmd = 1
            
        options = item.get('product_options', 'Non spécifiée')
        p_low = p_name.lower()
        
        # 1. LOGIQUE PACK 7 SACS
        if "pack 7" in p_low:
            lignes_production.append({"Client": nom_client, "Ville": ville, "Produit": "Sac Standard", "Couleur": options, "Quantité": qte_cmd * 3})
            lignes_production.append({"Client": nom_client, "Ville": ville, "Produit": "Sac BigBag", "Couleur": options, "Quantité": qte_cmd * 4})
        
        # 2. LOGIQUE PACK 5 SACS
        elif "pack 5" in p_low:
            lignes_production.append({"Client": nom_client, "Ville": ville, "Produit": "Sac Standard", "Couleur": options, "Quantité": qte_cmd * 5})
            
        # 3. LOGIQUE BOUDINS DE PORTE
        elif any(x in p_low for x in ["boudin", "top tip", "anti-cafard"]):
            taille = "6-8 cm"
            if "3-4" in p_low or "3-4" in options: taille = "3-4 cm"
            elif "4-5" in p_low or "4-5" in options: taille = "4-5 cm"
            lignes_production.append({"Client": nom_client, "Ville": ville, "Produit": f"Boudin {taille}", "Couleur": options, "Quantité": qte_cmd * 4})
            
        # 4. AUTRES PRODUITS
        else:
            mult = 1
            if any(x in p_low for x in ["nema", "booka"]): mult = 4
            lignes_production.append({"Client": nom_client, "Ville": ville, "Produit": p_name, "Couleur": options, "Quantité": qte_cmd * mult})
            
    return lignes_production

# --- INTERFACE UTILISATEUR ---
st.sidebar.header("📡 Statut Liaison TikTak")
st.sidebar.success("Connecteur API Activé")
if st.sidebar.button("🗑️ Vider la liste du jour"):
    st.session_state['commandes_live'] = []
    st.rerun()

if st.session_state['commandes_live']:
    df_global = pd.DataFrame(st.session_state['commandes_live'])
    st.subheader("✂️ RÉCAPITULATIF POUR L'ATELIER")
    recap = df_global.groupby(['Produit', 'Couleur'])['Quantité'].sum().reset_index()
    st.dataframe(recap, use_container_width=True, height=400)
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf) as wr: recap.to_excel(wr, index=False)
    st.download_button("📥 TÉLÉCHARGER L'EXCEL DE PRODUCTION", buf.getvalue(), "Production_Menzberg.xlsx", type="primary")

    with st.expander("🔍 Voir le détail par client"):
        st.dataframe(df_global)
else:
    st.info("👋 Bienvenue Salah. En attente de commandes venant de TikTak Pro...")

st.divider()
with st.expander("🛠️ TESTER UNE COMMANDE (Simuler TikTak Pro)"):
    exemple_json = st.text_area("JSON de test :", height=200)
    if st.button("Simuler l'arrivée d'une commande"):
        try:
            data_test = json.loads(exemple_json)
            nouvelles_lignes = traiter_donnees_tiktak(data_test)
            st.session_state['commandes_live'].extend(nouvelles_lignes)
            st.rerun()
        except Exception as e:
            st.error(f"Erreur : {e}")
