import streamlit as st

# --- PAGE SETUP ---    
about_page = st.Page(
    page="views/about_me.py",
    title="Napoli ATTIVA",
    icon="🏙️", 
    default=True,
)
project_1_page = st.Page(
    page="views/sales_dashboard.py",
    title="Sales Dashboard",
    icon="📊",  
)
project_2_page = st.Page(
    page="views/chatbot.py",
    title="Chatbot",
    icon="🤖",  
)


# --- NAVIGATION SETUP ---
pg = st.navigation(
    {
        "Info":[about_page],
        "Projects": [project_1_page, project_2_page]
        }
    )

# --- RUN NAVIGATION ---
pg.run()

st.logo('assets/logoNapoliAttiva.jpg',size= "large")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] img {
            height: 200px !important;
            width: 400px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

