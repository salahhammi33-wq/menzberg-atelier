import streamlit as st
import pandas as pd
import io, re

st.set_page_config(page_title="Menzberg Production", layout="wide")

# Initialisation de la mémoire
if 'prod_data' not in st.session_state:
    st.session_state['prod_data'] = []

st.title("🚀 Menzberg : Saisie Rapide Atelier")

# --- ZONE DE SAISIE ---
st.subheader("📝 Copier-Coller depuis TikTak")
input_text = st.text_area("Colle ici le texte de tes commandes :", height=150, 
                         placeholder="Exemple : Pack 7 Sacs - Gris - 2\nBoudin anti-cafard - Marron - 1")

if st.button("➕ Ajouter à la production", type="primary"):
    lines = input_text.split('\n')
    new_entries = []
    
    for line in lines:
        if not line.strip(): continue
        
        # Extraction simplifiée de la quantité : on cherche juste le dernier nombre dans la ligne
        nombres = re.findall(r'\d+', line)
        qte = int(nombres[-1]) if nombres else 1
        
        line_low = line.lower()
        
        # Détection Couleur
        couleur = "Standard"
        for c in ["gris", "marron", "noir", "bleu", "beige", "chocolat", "anthracite"]:
            if c in line_low: couleur = c.capitalize()

        # LOGIQUE DE CONVERSION MENZBERG
        if "pack 7" in line_low:
            new_entries.append({"Produit": "Sac Standard", "Couleur": couleur, "Qte": qte * 3})
            new_entries.append({"Produit": "Sac BigBag", "Couleur": couleur, "Qte": qte * 4})
        elif "pack 5" in line_low:
            new_entries.append({"Produit": "Sac Standard", "Couleur": couleur, "Qte": qte * 5})
        elif any(x in line_low for x in ["boudin", "anti-cafard"]):
            new_entries.append({"Produit": "Boudin Porte", "Couleur": couleur, "Qte": qte * 4})
        else:
            # Nettoyage du nom du produit (on garde ce qui est avant le premier tiret ou chiffre)
            nom_propre = re.split(r'[-–\d]', line)[0].strip()
            new_entries.append({"Produit": nom_propre[:30], "Couleur": couleur, "Qte": qte})

    st.session_state['prod_data'].extend(new_entries)
    st.success(f"Ajouté avec succès !")

# --- AFFICHAGE RESULTATS ---
if st.session_state['prod_data']:
    df = pd.DataFrame(st.session_state['prod_data'])
    
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Total à fabriquer")
        recap = df.groupby(['Produit', 'Couleur'])['Qte'].sum().reset_index()
        st.dataframe(recap, use_container_width=True)
    
    with col2:
        st.subheader("⚙️ Actions")
        if st.button("🗑️ Vider tout"):
            st.session_state['prod_data'] = []
            st.rerun()
            
        buf = io.BytesIO()
        with pd.ExcelWriter(buf) as wr: recap.to_excel(wr, index=False)
        st.download_button("📥 Télécharger Excel", buf.getvalue(), "Production_Menzberg.xlsx")
