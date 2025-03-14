import streamlit as st
from PIL import Image
import base64
import pandas as pd
import folium
from streamlit_folium import folium_static

# Page configuration
st.set_page_config(
    page_title="NAPOLI ATTIVA",
    page_icon="🏙️",
    layout="wide",
)

# Custom CSS per lo stile napoletano
st.markdown("""
<style>
    body {
        font-family: 'Arial', sans-serif;
        background: url('https://www.ilmioviaggioa.com/wp-content/uploads/2023/07/migliori-esperienze-da-fare-a-napoli1-1024x683.jpg') no-repeat center center fixed;
        background-size: cover;
    }
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        color: #00A1E4;  /* Azzurro Napoli */
        text-align: center;
        margin-bottom: 1.5rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
    }
    .sub-header {
        font-size: 1.8rem;
        color: #005F9E;  /* Blu più scuro */
        text-align: center;
        margin-bottom: 2rem;
    }
    .highlight {
        background: linear-gradient(135deg, #00A1E4, #0051A1);  /* Sfumatura di azzurro */
        padding: 20px;
        border-radius: 8px;
        color: white;
        text-align: center;
        font-size: 1.2rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stat-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        width: 100%;
        height: 120px;
        min-height: 100px;
        max-height: 150px;
        border-top: 4px solid #00A1E4;  /* Bordo superiore azzurro */
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00A1E4;  /* Azzurro Napoli */
    }
    .stat-label {
        font-size: 1rem;
        color: #555;
    }
    .card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #00A1E4;  /* Bordo laterale azzurro */
    }
    .button-style {
        background-color: #00A1E4;
        color: white;
        font-size: 1.2rem;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
    }
            
    div.stButton > button {
        background-color: #00A1E4;  /* Azzurro Napoli */
        color: white;
        font-weight: bold;
        font-size: 16px;
        padding: 12px 24px;
        border-radius: 8px;
        border: none;
        width: 100%;
        transition: all 0.3s;
        text-transform: uppercase;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        background-color: #D1001F;  /* Rosso Napoli per contrasto */
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        cursor: pointer;
    }
    
    div.stButton > button:active {
        transform: translateY(2px);
    }
    
    /* Stile sidebar */
    .sidebar .sidebar-content {
        background-color: #f2f7fa;
    }
    
            
    .napoli-footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        font-size: 0.9rem;
        color: #666;
        border-top: 2px solid #00A1E4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>NAPOLI ATTIVA</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='sub-header'>Applicazione di Segnalazioni Cittadine</h2>", unsafe_allow_html=True)

# Welcome section con frase in napoletano
st.markdown("""
<div class='highlight'>
    <h3>BENVENUTI IN NAPOLI ATTIVA</h3>
    <p>Jamm' ja! Insieme possiamo migliorare la nostra bella città segnalando i problemi in tempo reale.</p>
</div>
""", unsafe_allow_html=True)

# Dashboard statistics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-number'>1,234</div>
        <div class='stat-label'>Segnalazioni Totali</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-number'>782</div>
        <div class='stat-label'>Segnalazioni Risolte</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-number'>328</div>
        <div class='stat-label'>In Lavorazione</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='stat-box'>
        <div class='stat-number'>124</div>
        <div class='stat-label'>Segnalazioni Nuove</div>
    </div>
    """, unsafe_allow_html=True)

# Call to action con frase in napoletano
st.markdown("### Fai 'na Segnalazione")

if st.button("INVIA NUOVA SEGNALAZIONE", use_container_width=True):
    # Reindirizza a chatbot.py
    st.switch_page("views/chatbot.py")


# Sidebar with login and filters
with st.sidebar:
    st.markdown("### Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    st.button("Accedi")
    
    st.markdown("### Filtri")
    st.multiselect("Categorie", ["Strade", "Parchi", "Rifiuti", "Traffico", "Altre"])
    st.selectbox("Quartiere", ["Tutti", "Centro Storico", "Chiaia", "Vomero", "Fuorigrotta", "Posillipo", "Bagnoli"])
    st.selectbox("Stato", ["Tutti", "Nuova", "Assegnata", "In lavorazione", "Risolta", "Chiusa"])
    st.date_input("Da data")
    st.date_input("A data")
    st.button("Applica Filtri")

#Footer
st.markdown("""
<div class='napoli-footer'>
    <p>© 2025 NAPOLI ATTIVA - 'A Piattaforma d''e Segnalazioni d''a Città</p>
    <p>Forza Napoli Sempre! 💙</p>
</div>
""", unsafe_allow_html=True)