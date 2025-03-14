import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import plotly.express as px

# Layout della pagina
st.set_page_config(page_title="Dashboard Segnalazioni", layout="wide")

# Titolo della dashboard
st.title("📊 Dashboard delle Segnalazioni Urbane")

# Statistiche principali
st.markdown("## 📌 Statistiche in Tempo Reale")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Segnalazioni Totali", value="1,234", delta="+45 rispetto alla scorsa settimana")
with col2:
    st.metric(label="Segnalazioni Risolte", value="782", delta="+30")
with col3:
    st.metric(label="In Lavorazione", value="328", delta="-12")
with col4:
    st.metric(label="Segnalazioni Nuove", value="124", delta="+27")

# Grafico delle segnalazioni per categoria
st.markdown("## 📈 Distribuzione delle Segnalazioni")
data_pie = pd.DataFrame({
    "Categoria": ["Strade", "Rifiuti", "Parchi", "Traffico", "Altre"],
    "Numero": [450, 320, 210, 150, 104]
})
category_colors = {"Strade": "#E63946", "Rifiuti": "#F4A261", "Parchi": "#2A9D8F", "Traffico": "#264653", "Altre": "#8A4FFF"}
fig_pie = px.pie(data_pie, names='Categoria', values='Numero', title='Distribuzione per Categoria', 
                 color='Categoria', color_discrete_map=category_colors)
st.plotly_chart(fig_pie, use_container_width=True)

# Mappa delle segnalazioni
st.markdown("## 🗺️ Mappa delle Segnalazioni")

map_data = [
    {"lat": 40.8401, "lon": 14.2516, "category": "Strade", "desc": "Buca profonda in Via Toledo", "status": "In lavorazione"},
    {"lat": 40.8470, "lon": 14.2513, "category": "Rifiuti", "desc": "Cassonetti non svuotati in Piazza Dante", "status": "Risolto"},
    {"lat": 40.8344, "lon": 14.2351, "category": "Parchi", "desc": "Panchine rotte alla Villa Comunale", "status": "Assegnato"},
    {"lat": 40.8517, "lon": 14.2720, "category": "Traffico", "desc": "Semaforo non funzionante a Piazza Garibaldi", "status": "In attesa"},
    {"lat": 40.8367, "lon": 14.2450, "category": "Strade", "desc": "Marciapiede dissestato in Via Chiaia", "status": "Risolto"},
    {"lat": 40.8550, "lon": 14.2427, "category": "Rifiuti", "desc": "Discarica abusiva in Vico San Pietro", "status": "Nuova"},
    {"lat": 40.8322, "lon": 14.2388, "category": "Parchi", "desc": "Giochi danneggiati al Parco Virgiliano", "status": "In lavorazione"},
]

m = folium.Map(location=[40.8333, 14.2500], zoom_start=14)
category_colors = {"Strade": "red", "Rifiuti": "green", "Parchi": "darkgreen", "Traffico": "orange", "Altre": "blue"}

for point in map_data:
    html = f"""
    <div style='font-family:sans-serif;'>
        <h4>{point['category']}</h4>
        <p><b>Descrizione:</b> {point['desc']}</p>
        <p><b>Stato:</b> {point['status']}</p>
    </div>
    """
    color = category_colors.get(point['category'], 'blue')
    folium.Marker(
        [point['lat'], point['lon']], 
        popup=folium.Popup(html, max_width=300),
        icon=folium.Icon(color=color, icon="info-sign")
    ).add_to(m)

folium_static(m)

# Grafico dell'andamento settimanale
st.markdown("## 📊 Andamento delle Segnalazioni Settimanali")
trend_data = pd.DataFrame({
    "Giorno": ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"],
    "Numero": [120, 150, 180, 140, 160, 130, 110]
})
fig_trend = px.line(trend_data, x='Giorno', y='Numero', markers=True, title='Numero di Segnalazioni negli Ultimi 7 Giorni')
st.plotly_chart(fig_trend, use_container_width=True)

# Tabella delle ultime segnalazioni
st.markdown("## 📝 Ultime Segnalazioni")
data = {
    'Data': ['12/03/2025', '11/03/2025', '10/03/2025', '09/03/2025', '08/03/2025'],
    'Categoria': ['Strade', 'Rifiuti', 'Parchi', 'Traffico', 'Strade'],
    'Descrizione': [
        'Buca profonda in Via Toledo', 
        'Cassonetti non svuotati in Piazza Dante', 
        'Panchine rotte alla Villa Comunale', 
        'Semaforo non funzionante a Piazza Garibaldi', 
        'Marciapiede dissestato in Via Chiaia'
    ],
    'Stato': ['In lavorazione', 'Risolto', 'Assegnato', 'In attesa', 'Risolto']
}
df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)
