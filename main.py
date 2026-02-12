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
input_text = st.text_area("Colle ici le texte de tes commandes (même en vrac) :", height=150, 
                         placeholder="Exemple : Pack 7 Sacs - Gris - Qté: 2\nBoudin anti-cafard - Marron - 1")

if st.button("➕ Ajouter à la production", type="primary"):
    lines = input_text.split('\n')
    new_entries = []
    
    for line in lines:
        if not line.strip(): continue
        
        # Extraction intelligente de la quantité (cherche un chiffre isolé ou après 'x' ou ':')
        qte_match = re.search(r'(\d+)(?=\s*$|(?:\s*Qté|\s*x))|(?<=x\s*)(\d+)', line, re.IGNORECASE)
        qte = int(qte_match.group(0)) if qte_match else 1
        
        line_low = line.lower()
        
        # Détection Couleur (cherche les mots classiques)
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
            # Pour les produits unitaires (Nema, Booka, etc.)
            new_entries.append({"Produit": line.split('-')[0].strip()[:20], "Couleur": couleur, "Qte": qte})

    st.session_state['prod_data'].extend(new_entries)
    st.success(f"{len(new_entries)} lignes ajoutées !")

# --- AFFICHAGE RESULTATS ---
if st.session_state['prod_data']:
    df = pd.DataFrame(st.session_state['prod_data'])
    
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Total à fabriquer")
        recap = df.groupby(['Produit', 'Couleur'])['Qte'].sum().reset_index()
        st.table(recap)
    
    with col2:
        st.subheader("⚙️ Actions")
        if st.button("🗑️ Vider tout"):
            st.session_state['prod_data'] = []
            st.rerun()
            
        buf = io.BytesIO()
        with pd.ExcelWriter(buf) as wr: recap.to_excel(wr, index=False)
        st.download_button("📥 Télécharger l'ordre de coupe (Excel)", buf.getvalue(), "Production_Menzberg.xlsx")
