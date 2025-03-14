import streamlit as st
import base64
import httpx
import boto3
from langchain_aws import ChatBedrock
from botocore.config import Config
import urllib3
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from fpdf import FPDF
import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Union
import json
import re

# Disabilita avvisi SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Pydantic model per la segnalazione
class RiskAssessment(BaseModel):
    data: datetime.datetime = Field(default_factory=datetime.datetime.now)
    location: Optional[str] = Field(default=None, description="Localizzazione della segnalazione")
    raccomandazione: str = Field(description="Raccomandazione per l'amministrazione comunale")
    livello_pericolosita: Literal[1, 2, 3] = Field(description="Livello di pericolosità (1=Basso, 2=Medio, 3=Alto)")
    descrizione: str = Field(description="Descrizione dettagliata della segnalazione")
    categoria: Literal["Strada Pubblica", "Verde Urbano", "Edifici e Infrastrutture", "Altre criticità"] = Field(
        description="Categoria della segnalazione"
    )

# Configura il client Bedrock
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='eu-west-1',
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    verify=False,  # Disabilita la verifica SSL
    config=Config(proxies={'https': None})
)

# Inizializza il modello
llm_bedrock = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    client=bedrock_client,
    model_kwargs={"temperature": 0.7, "max_tokens": 2000}
)

# Inizializza la cronologia della chat nella sessione se non esiste già
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="Sei un assistente comunale che aiuta i cittadini con informazioni e segnalazioni. Rispondi in italiano.")
    ]

# Inizializza le variabili di sessione per la gestione delle immagini
if "image_data" not in st.session_state:
    st.session_state.image_data = None
if "image_source" not in st.session_state:
    st.session_state.image_source = None

# Streamlit UI con tabs
st.title("Assistente Comunale AI")

tabs = st.tabs(["Chat Generale 💬", "Valutazione Rischio ⚠️"])

with tabs[1]:
    st.header("Valutatore di Rischio")
    
    # Input per la localizzazione
    location_input = st.text_input("Inserisci la localizzazione (opzionale)", "")
    
    # Radio button per selezionare la fonte dell'immagine
    image_source = st.radio(
        "Seleziona la fonte dell'immagine:",
        ["Carica un'immagine", "Scatta una foto"],
        horizontal=True
    )
    st.session_state.image_source = image_source
    
    # Gestione dell'immagine in base alla fonte selezionata
    if image_source == "Carica un'immagine":
        uploaded_file = st.file_uploader("Carica un'immagine per la valutazione del rischio", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            st.session_state.image_data = base64.b64encode(uploaded_file.read()).decode("utf-8")
            st.image(uploaded_file, caption="Immagine caricata", use_container_width=True)
        elif st.session_state.image_source != "Carica un'immagine":
            st.session_state.image_data = None
    else:  # "Scatta una foto"
        camera_col1, camera_col2 = st.columns([3, 1])
        with camera_col1:
            captured_image = st.camera_input("Scatta una foto")
        with camera_col2:
            if captured_image is not None:
                st.session_state.image_data = base64.b64encode(captured_image.read()).decode("utf-8")
                if st.button("❌ Cancella foto", key="clear_camera"):
                    st.session_state.image_data = None
                    st.rerun()
    
    # Mostra avviso se non c'è immagine
    if st.session_state.image_data is None:
        st.warning("Carica un'immagine o scatta una foto per ottenere una valutazione.")

    # Definisci il prompt template
    prompt_template = PromptTemplate(
        input_variables=[],
        template="""
        Analizza l'immagine e assegna un livello di rischio:
        - Basso rischio (1): Il problema non rappresenta un pericolo immediato ma richiede intervento per prevenire danni futuri.
        - Medio rischio (2): Il problema può causare disagi e potenziali incidenti se non risolto in tempi brevi.
        - Alto rischio (3): Il problema rappresenta un pericolo immediato per la sicurezza pubblica e richiede un intervento urgente.
        
        Categorie di valutazione:
        1. Strada Pubblica
        2. Verde Urbano
        3. Edifici e Infrastrutture
        4. Altre criticità (illuminazione, segnaletica, sicurezza urbana)
        
        Fornisci la risposta in formato JSON strutturato con i seguenti campi:
        - livello_pericolosita: numero intero da 1 a 3
        - categoria: una delle categorie elencate sopra
        - descrizione: descrizione dettagliata del problema
        - raccomandazione: suggerimento chiaro per l'amministrazione comunale
        
        Assicurati che il JSON sia valido e correttamente formattato.
        """.strip()
    )

    def extract_json_from_text(text):
        """Estrae il JSON dalla risposta di testo."""
        # Cerca un pattern JSON nella risposta
        json_pattern = r'\{[\s\S]*\}'
        match = re.search(json_pattern, text)
        
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

    def create_pdf_report(assessment):
        """Crea un report PDF basato sulla valutazione."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Intestazione
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, "Report di Valutazione del Rischio", ln=True, align='C')
        pdf.ln(10)
        
        # Contenuto
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, f"Data: {assessment.data.strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        
        if assessment.location:
            pdf.cell(0, 10, f"Localizzazione: {assessment.location}", ln=True)
        
        pdf.cell(0, 10, f"Categoria: {assessment.categoria}", ln=True)
        
        # Livello di pericolosità con colore
        risk_level_text = {1: "Basso", 2: "Medio", 3: "Alto"}
        pdf.cell(0, 10, f"Livello di Pericolosità: {risk_level_text[assessment.livello_pericolosita]}", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, "Descrizione:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, assessment.descrizione)
        
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, "Raccomandazione:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, assessment.raccomandazione)
        
        # Salvataggio del PDF
        pdf_filename = f"report_rischio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(pdf_filename)
        
        return pdf_filename

    if st.session_state.image_data and st.button("Valuta Rischio ⚠️"):
        with st.spinner("Analizzando l'immagine..."):
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt_template.format()},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.image_data}"}},
                ],
            )
            
            response = llm_bedrock.invoke([message])
            
            # Estrai il JSON dalla risposta
            json_data = extract_json_from_text(response.content)
            
            if json_data:
                # Crea l'oggetto Pydantic
                assessment = RiskAssessment(
                    data=datetime.datetime.now(),
                    location=location_input if location_input else None,
                    raccomandazione=json_data.get("raccomandazione", ""),
                    livello_pericolosita=json_data.get("livello_pericolosita", 1),
                    descrizione=json_data.get("descrizione", ""),
                    categoria=json_data.get("categoria", "Altre criticità")
                )
                
                # Visualizza i risultati
                st.subheader("Risultati della Valutazione")
                
                # Mostra il livello di rischio con un colore appropriato
                risk_colors = {1: "green", 2: "orange", 3: "red"}
                risk_labels = {1: "Basso Rischio", 2: "Medio Rischio", 3: "Alto Rischio"}
                
                st.markdown(
                    f"<div style='background-color: {risk_colors[assessment.livello_pericolosita]}; padding: 10px; border-radius: 5px; color: white;'>"
                    f"<h3>{risk_labels[assessment.livello_pericolosita]}</h3></div>",
                    unsafe_allow_html=True
                )
                
                st.markdown(f"**Categoria:** {assessment.categoria}")
                if assessment.location:
                    st.markdown(f"**Localizzazione:** {assessment.location}")
                
                st.subheader("Descrizione")
                st.write(assessment.descrizione)
                
                st.subheader("Raccomandazione")
                st.write(assessment.raccomandazione)
                
                # Crea e fornisci il PDF per il download
                pdf_file = create_pdf_report(assessment)
                
                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="📄 Scarica il Report PDF",
                        data=file,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )
            else:
                st.error("Non è stato possibile estrarre dati strutturati dalla risposta. Mostrando la risposta grezza:")
                st.markdown(response.content)


# --- PAGINA CHAT GENERALE ---
with tabs[0]:
    st.header("Chat con l'Assistente Comunale")
    
    # Visualizza la cronologia della chat
    for message in st.session_state.messages[1:]:  # Salta il messaggio di sistema
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                # Gestisci il contenuto che potrebbe essere testo o una lista di contenuti multimodali
                if isinstance(message.content, str):
                    st.write(message.content)
                else:
                    # Per messaggi multimodali, visualizza solo il testo
                    for item in message.content:
                        if item.get("type") == "text":
                            st.write(item.get("text", ""))
                        elif item.get("type") == "image_url":
                            st.image(item.get("image_url", {}).get("url", ""))
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)
    
    # Input per la chat
    user_input = st.chat_input("Scrivi qui la tua domanda...")
    
    # Opzione per allegare un'immagine nella chat
    with st.expander("Allega un'immagine alla domanda"):
        chat_image = st.file_uploader("Carica un'immagine", type=["jpg", "jpeg", "png"], key="chat_image")

    if user_input:
        # Crea il contenuto del messaggio in base alla presenza o meno di un'immagine
        if chat_image:
            image_data = base64.b64encode(chat_image.read()).decode("utf-8")
            message_content = [
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        else:
            message_content = user_input
        
        # Aggiungi il messaggio dell'utente alla cronologia
        user_message = HumanMessage(content=message_content)
        st.session_state.messages.append(user_message)
        
        # Visualizza il messaggio dell'utente
        with st.chat_message("user"):
            st.write(user_input)
            if chat_image:
                st.image(chat_image, width=300)
        
        # Ottieni la risposta dal modello
        with st.spinner("L'assistente sta scrivendo..."):
            response = llm_bedrock.invoke(st.session_state.messages)
            
            # Aggiungi la risposta dell'assistente alla cronologia
            st.session_state.messages.append(response)
            
            # Visualizza la risposta dell'assistente
            with st.chat_message("assistant"):
                st.write(response.content)

    if user_input:
        # Rilevamento della richiesta di segnalazione
        if "segnalazione" in user_input.lower() or "rischio" in user_input.lower() or "pericolo" in user_input.lower():
            # Risposta del chatbot con reindirizzamento
            response_content = "Per effettuare una segnalazione, vai alla scheda 'Valutazione Rischio' ⚠️."
            
            # Aggiungi il messaggio dell'utente e la risposta del chatbot alla cronologia
            user_message = HumanMessage(content=user_input)
            assistant_message = AIMessage(content=response_content)
            st.session_state.messages.append(user_message)
            st.session_state.messages.append(assistant_message)
            
            # Visualizza il messaggio dell'utente
            with st.chat_message("user"):
                st.write(user_input)
            
            # Visualizza la risposta del chatbot
            with st.chat_message("assistant"):
                st.write(response_content)
            
            # Pulsante per reindirizzare alla tab "Valutazione Rischio"
            if st.button("Vai a Valutazione Rischio ⚠️"):
                tabs[1].__enter__() #simula il click sulla tab 0
                st.rerun()
                
        else:
            # Aggiungi il messaggio dell'utente alla cronologia
            user_message = HumanMessage(content=message_content)
            st.session_state.messages.append(user_message)
            
            # Visualizza il messaggio dell'utente
            with st.chat_message("user"):
                st.write(user_input)
                if chat_image:
                    st.image(chat_image, width=300)
            
            # Ottieni la risposta dal modello
            with st.spinner("L'assistente sta scrivendo..."):
                response = llm_bedrock.invoke(st.session_state.messages)
                
                # Aggiungi la risposta dell'assistente alla cronologia
                st.session_state.messages.append(response)
                
                # Visualizza la risposta dell'assistente
                with st.chat_message("assistant"):
                    st.write(response.content)

    