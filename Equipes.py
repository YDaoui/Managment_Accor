import streamlit as st
import mysql.connector
import os
import plotly.express as px
from PIL import Image
from datetime import datetime
from dateutil.relativedelta import relativedelta
from contextlib import closing
import pandas as pd
from db_utils import get_user_name, display_logo, authenticate, get_user_status, login_page, get_db_connection

# Ajout de CSS personnalisé
def add_custom_css():
    """Ajoute du CSS personnalisé à l'interface Streamlit."""
    custom_css = """
    <style>
    footer {visibility: hidden;}
    .stButton>button {
        background-color: #bb8654;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #ffe7ad;
        color: #bb8654;
    }
    .stSelectbox>div>div>input {
        background-color: #ffe7ad;
        color: #bb8654;
    }
    .stSelectbox>div>div>input:focus {
        background-color: #bb8654;
        color: white;
    }
    .stSelectbox label {
        color: #b28765;
    }
    .sidebar .option-menu {
        background-color: #040233;
        color: white;
        padding: 20px;
        height: 100vh;
        overflow: auto;
    }
    .sidebar .option-menu .nav-link {
        color: white;
        font-size: 16px;
        text-align: left;
        padding: 10px;
        cursor: pointer;
    }
    .sidebar .option-menu .nav-link-selected {
        background-color: #b28765;
        color: white;
    }
    .custom-title {
        background-image: linear-gradient(to left, #bb8654, #ffffff);
        color: #040233;
        padding: 40px;
        border-radius: 5px;
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        height: 160px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .card {
        background-size: cover;
        background-position: center;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-shadow: 2px 2px 4px #000000;
        margin: 10px;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .classic {
        background-color: #1f77b4;
    }
    .silver {
        background-color: #c0c0c0;
    }
    .gold {
        background-color: #ffd700;
    }
    .platinum {
        background-color: #e5e4e2;
    }
    .card h3 {
        font-size: 28px;
        margin-bottom: 10px;
    }
    .card p {
        font-size: 24px;
        margin: 5px 0;
    }
    .card .montant {
        font-size: 24px;
        font-weight: bold;
    }
    .card .ventes {
        font-size: 20px;
        font-weight: bold;
    }
    .arrow {
        font-size: 24px;
        font-weight: bold;
    }
    .arrow-up {
        color: green;
    }
    .arrow-down {
        color: red;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Fonction pour calculer l'âge
def calculate_age(birth_date):
    today = datetime.now()
    delta = relativedelta(today, birth_date)
    return f"{delta.years} (Ans)"

# Fonction pour calculer l'ancienneté
def calculate_anciennete(date_in):
    today = datetime.now()
    delta = relativedelta(today, date_in)
    return f"{delta.years} (Ans) {delta.months} (Mois) {delta.days} (Jours)"

# Récupérer les agents de l'équipe du manager connecté
def fetch_team_agents(conn, manager_name):
    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            query = """
                SELECT ID_Citrix, Nom_prenom 
                FROM effectifs 
                WHERE Team = %s AND Statut = 'Agent'
            """
            cursor.execute(query, (manager_name,))
            agents = cursor.fetchall()
            return agents
    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la récupération des agents : {err}")
        return []

# Récupérer les ventes des agents
def fetch_agent_sales(conn, agent_id, start_date, end_date):
    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            query = """
                SELECT Date_Vente, Montant, Offre, Rate 
                FROM ventes 
                WHERE ID_Citrix = %s AND DATE(Date_Vente) BETWEEN %s AND %s
            """
            cursor.execute(query, (agent_id, start_date, end_date))
            sales = cursor.fetchall()
            return sales
    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la récupération des ventes : {err}")
        return []

# Fonction pour déterminer l'évolution des ventes
def determine_evolution(sales_df, offre):
    """Détermine si les ventes sont en hausse ou en baisse pour une offre donnée."""
    # Filtrer les ventes pour l'offre spécifique
    offre_sales = sales_df[sales_df["Offre"] == offre]
    
    # Trier par date
    offre_sales = offre_sales.sort_values(by="Date_Vente")
    
    # Calculer la tendance (hausse ou baisse)
    if len(offre_sales) > 1:
        montant_start = offre_sales.iloc[0]["Montant"]
        montant_end = offre_sales.iloc[-1]["Montant"]
        if montant_end > montant_start:
            return "↑", "green"  # Hausse
        elif montant_end < montant_start:
            return "↓", "red"  # Baisse
    return "", "black"  # Stable ou pas assez de données

# Page principale pour afficher les agents et leurs ventes
def page_equipes():
    add_custom_css()
    """Page pour afficher les membres de l'équipe et leurs performances."""
    # Afficher le logo de l'entreprise
    col1, col2 = st.columns([1, 5])
    with col1:
        display_logo(os.path.join("Images", "AC1.png"), width=160)
    with col2:
        st.markdown('<div class="custom-title">Résultat Equipe</div>', unsafe_allow_html=True)

    # Sélection des dates
    col1, col2, col3 = st.columns([4, 4, 4])
    with col1:
        start_date = st.date_input("Date de début", datetime.now(), key="start_date")
    with col2:
        end_date = st.date_input("Date de fin", datetime.now(), key="end_date")

    if start_date > end_date:
        st.error("La date de fin ne peut pas être antérieure à la date de début.")
        return

    # Connexion à la base de données
    conn = get_db_connection()
    if not conn:
        st.error("Erreur de connexion à la base de données.")
        return

    # Récupérer les agents de l'équipe du manager connecté
    manager_name = st.session_state.get("Nom_Prenom")
    agents = fetch_team_agents(conn, manager_name)
    if not agents:
        st.warning(f"Aucun agent trouvé dans votre équipe : {manager_name}.")
        return

    # Sélection de l'agent
    with col3:
        agent_names = [agent["Nom_prenom"] for agent in agents]
        selected_agent = st.selectbox("Sélectionnez un agent", agent_names, key="agent_select")
        selected_agent_id = next(agent["ID_Citrix"] for agent in agents if agent["Nom_prenom"] == selected_agent)

    # Récupérer les ventes de l'agent sélectionné
    sales_data = fetch_agent_sales(conn, selected_agent_id, start_date, end_date)
    if not sales_data:
        st.warning(f"Aucune donnée de vente trouvée pour {selected_agent} entre {start_date} et {end_date}.")
        return

    # Convertir les données en DataFrame
    sales_df = pd.DataFrame(sales_data)
    sales_by_offer_sum = sales_df.groupby('Offre')['Montant'].sum().reset_index()
    sales_by_offer_count = sales_df.groupby('Offre').size().reset_index(name='Nombre de Ventes')
    sales_by_offer = pd.merge(sales_by_offer_sum, sales_by_offer_count, on='Offre')

    # Afficher les cartes avec les flèches d'évolution
    col1, col2, col3, col4 = st.columns(4)
    for offre, col, css_class in zip(
        ["Club-Accor_Classic", "Club-Accor_Silver", "Club-Accor_Gold", "Club-Accor_Platinum"],
        [col1, col2, col3, col4],
        ["classic", "silver", "gold", "platinum"]
    ):
        if offre in sales_by_offer["Offre"].values:
            total_ventes = sales_by_offer[sales_by_offer["Offre"] == offre]["Nombre de Ventes"].values[0]
            total_montant = sales_by_offer[sales_by_offer["Offre"] == offre]["Montant"].values[0]

            # Déterminer l'évolution des ventes
            arrow, arrow_color = determine_evolution(sales_df, offre)

            # Afficher la carte
            col.markdown(
                f"""
                <div class="card {css_class}">
                    <h3>{offre}</h3>
                    <p>{total_ventes} ventes <span class="arrow" style="color: {arrow_color}; font-weight: bold;">{arrow}</span></p>
                    <p>{total_montant:.2f} €</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Afficher les graphiques et le tableau des ventes
    if sales_data:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Ventes par Heure (par Type d'Offre)")
            sales_df['Heure'] = sales_df['Date_Vente'].dt.hour
            sales_by_hour_offer = sales_df.groupby(['Heure', 'Offre'])['Montant'].sum().reset_index()
            fig_scatter = px.scatter(
                sales_by_hour_offer,
                x="Heure",
                y="Montant",
                color="Offre",
                title="Ventes par Heure (Classic, Silver, Gold, Platinum)",
                labels={"Montant": "Montant des Ventes", "Heure": "Heure de la Journée"},
                hover_data={"Montant": ":,.2f"},
                size_max=20
            )
            fig_scatter.update_traces(marker=dict(size=12))
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col2:
            st.subheader("Détail des Ventes")
            st.dataframe(sales_df.style.format({'Montant': '{:,.2f} €', 'Date_Vente': lambda x: x.strftime('%d/%m/%Y %H:%M')}), height=400)

    # Fermer la connexion à la base de données
    if conn.is_connected():
        conn.close()

# Exécuter la page
if __name__ == "__main__":
    page_equipes()