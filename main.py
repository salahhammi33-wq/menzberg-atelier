import streamlit as st
import pandas as pd
import json, io

# --- CONFIGURATION ---
st.set_page_config(page_title="Menzberg Live Hook", layout="wide")

# On utilise le cache pour garder les commandes même si la page est rafraîchie
if 'commandes_live' not in st.session_state:
    st.session_state['commandes_live'] = []

# --- FONCTION DE CALCUL MENZBERG ---
def traiter_donnees(data):
    lignes = []
    client = data.get('name', 'Client')
    for item in data.get('details', []):
        p_name = item.get('product_name', '')
        qte = int(item.get('quantity', 1))
        opt = item.get('product_options', 'Standard')
        p_low = p_name.lower()

        if "pack 7" in p_low:
            lignes.append({"Produit": "Sac Standard", "Couleur": opt, "Qte": qte * 3})
            lignes.append({"Produit": "Sac BigBag", "Couleur": opt, "Qte": qte * 4})
        elif "pack 5" in p_low:
            lignes.append({"Produit": "Sac Standard", "Couleur": opt, "Qte": qte * 5})
        elif any(x in p_low for x in ["boudin", "anti-cafard"]):
            lignes.append({"Produit": "Boudin Porte", "Couleur": opt, "Qte": qte * 4})
        else:
            lignes.append({"Produit": p_name, "Couleur": opt, "Qte": qte})
    return lignes

# --- RÉCEPTION DU WEBHOOK (La porte d'entrée) ---
# Cette partie permet à TikTak d'envoyer les infos directement
query_params = st.query_params
if "webhook" in query_params:
    # Note: Streamlit ne gère pas les POST directement facilement sans FastAPI, 
    # mais pour tester la liaison, on utilise la zone de simulation ci-dessous.
    pass

st.title("🛡️ Menzberg Atelier - Live")

# --- AFFICHAGE ---
if st.session_state['commandes_live']:
    df = pd.DataFrame(st.session_state['commandes_live'])
    st.subheader("📋 LISTE DE PRODUCTION")
    recap = df.groupby(['Produit', 'Couleur'])['Qte'].sum().reset_index()
    st.dataframe(recap, use_container_width=True)
    
    # Export
    buf = io.BytesIO()
    with pd.ExcelWriter(buf) as wr: recap.to_excel(wr, index=False)
    st.download_button("📥 Télécharger Excel", buf.getvalue(), "Production.xlsx")
else:
    st.info("En attente de commandes... Utilise la simulation ci-dessous pour tester.")

# --- ZONE DE TEST TIKTAK ---
st.divider()
with st.expander("🛠️ SIMULATION TIKTAK PRO (Copie ton JSON ici)"):
    json_input = st.text_area("Colle ici le JSON de TikTak :", height=200)
    if st.button("Lancer la simulation"):
        try:
            data = json.loads(json_input)
            res = traiter_donnees(data)
            st.session_state['commandes_live'].extend(res)
            st.rerun()
        except:
            st.error("Format JSON incorrect")
