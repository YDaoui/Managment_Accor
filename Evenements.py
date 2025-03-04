import streamlit as st
import mysql.connector
from PIL import Image
import os
from datetime import datetime
import pandas as pd
from streamlit_option_menu import option_menu
from contextlib import closing

#from db_utils import get_db_connection, get_user_name, display_logo, color_cells,login_page,authenticate,calculate_age,calculate_anciennete
from dateutil.relativedelta import relativedelta

from db_utils import get_db_connection, get_user_name, display_logo,calculate_age



def add_custom_css():
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
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def display_logo(image_path, width):
    try:
        img = Image.open(image_path)
        st.image(img, width=width)
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image : {e}")





def Evenement_page():
    col1, col2 = st.columns([1, 9])

    with col1:
        display_logo(os.path.join("Images", "th.jpeg"), width=120)

    with col2:
        st.header("Evénements")

    # Deuxième ligne de colonnes pour l'ID Citrix et la sélection des événements
    col1, col2 = st.columns([1, 4])
    with col1:
        # Zone de texte pour l'ID Citrix
        citrix_id = st.text_input("Taper l'ID Citrix")

        # Liste des options pour le combo box
        options = ["Chang.Equipe", "Chang.Statut", "Chang.Competence", "Chang.Site", "Formation", "Tutorat", "Cotec", "Depart"]

        # Premier combo box pour sélectionner un événement
        selection = st.selectbox("Sélectionner un Événement :", options)

        # Initialisation des variables
        selected_competence = None
        selected_statut = None
        selected_team = None
        selected_formation = None

        # Logique en fonction de l'événement sélectionné
        if selection == "Chang.Equipe" and citrix_id:
            add_custom_css()
            # Connexion à la base de données
            conn = get_db_connection()
            if not conn:
                st.error("Impossible de se connecter à la base de données.")
            else:
                try:
                    with closing(conn.cursor(dictionary=True)) as cursor:
                        # Récupérer l'équipe actuelle associée à l'ID Citrix
                        query = "SELECT team FROM effectifs WHERE ID_Citrix = %s"
                        cursor.execute(query, (citrix_id,))
                        current_team = cursor.fetchone()

                        if current_team:
                            current_team_name = current_team["team"]
                        else:
                            st.info(f"Aucune équipe trouvée pour l'ID Citrix {citrix_id}.")
                            current_team_name = None

                        # Récupérer toutes les équipes disponibles
                        query = "SELECT DISTINCT team FROM effectifs"
                        cursor.execute(query)
                        teams = cursor.fetchall()

                        if teams:
                            team_names = [team["team"] for team in teams]
                            if current_team_name:
                                team_names = [team for team in team_names if team != current_team_name]
                            selected_team = st.selectbox("Nouvelle équipe :", team_names)
                        else:
                            st.info("Aucune équipe trouvée.")
                except mysql.connector.Error as err:
                    st.error(f"Erreur lors de la récupération des équipes : {err}")
                finally:
                    conn.close()

        elif selection == "Chang.Statut" and citrix_id:
            # Connexion à la base de données pour changer le statut
            conn = get_db_connection()
            if not conn:
                st.error("Impossible de se connecter à la base de données.")
            else:
                try:
                    with closing(conn.cursor(dictionary=True)) as cursor:
                        # Récupérer le statut actuel associé à l'ID Citrix
                        query = "SELECT Statut FROM effectifs WHERE ID_Citrix = %s"
                        cursor.execute(query, (citrix_id,))
                        current_statut = cursor.fetchone()

                        if current_statut:
                            current_statut_name = current_statut["Statut"]
                        else:
                            st.info(f"Aucun statut trouvé pour l'ID Citrix {citrix_id}.")
                            current_statut_name = None

                        # Récupérer tous les statuts disponibles
                        query = "SELECT DISTINCT Statut FROM effectifs"
                        cursor.execute(query)
                        statuts = cursor.fetchall()

                        if statuts:
                            statut_names = [statut["Statut"] for statut in statuts]
                            if current_statut_name:
                                statut_names = [statut for statut in statut_names if statut != current_statut_name]
                            selected_statut = st.selectbox("Nouveau statut :", statut_names)
                        else:
                            st.info("Aucun statut trouvé.")
                except mysql.connector.Error as err:
                    st.error(f"Erreur lors de la récupération des statuts : {err}")
                finally:
                    conn.close()

        elif selection == "Chang.Competence" and citrix_id:
            # Connexion à la base de données pour changer la compétence
            conn = get_db_connection()
            if not conn:
                st.error("Impossible de se connecter à la base de données.")
            else:
                try:
                    with closing(conn.cursor(dictionary=True)) as cursor:
                        # Récupérer la compétence actuelle associée à l'ID Citrix
                        query = "SELECT Competence FROM effectifs WHERE ID_Citrix = %s"
                        cursor.execute(query, (citrix_id,))
                        current_competence = cursor.fetchone()

                        if current_competence:
                            current_Competence_name = current_competence["Competence"]
                        else:
                            st.info(f"Aucune compétence trouvée pour l'ID Citrix {citrix_id}.")
                            current_Competence_name = None

                        # Récupérer toutes les compétences disponibles
                        query = "SELECT DISTINCT Competence FROM effectifs"
                        cursor.execute(query)
                        competences = cursor.fetchall()

                        if competences:
                            competence_names = [competence["Competence"] for competence in competences]
                            if current_Competence_name:
                                competence_names = [competence for competence in competence_names if competence != current_Competence_name]
                            selected_competence = st.selectbox("Nouvelle compétence :", competence_names)
                        else:
                            st.info("Aucune compétence trouvée.")
                except mysql.connector.Error as err:
                    st.error(f"Erreur lors de la récupération des compétences : {err}")
                finally:
                    conn.close()

        elif selection == "Formation" and citrix_id:
            selected_formation = st.text_input("Nom de la Formation :")

    with col2:
    # Récupération des informations de l'utilisateur
        with col2:
    # Récupération des informations de l'utilisateur
            def get_team_members(citrix_id):
                conn = get_db_connection()
                if not conn:
                    return pd.DataFrame()

                try:
                    query = """
                        SELECT Nom_Prenom, UM, Team, Competence, Statut,Gender,Birth_Date, Date_In, Solde_Conge
                        FROM effectifs WHERE ID_Citrix = %s
                    """
                    df = pd.read_sql(query, conn, params=(citrix_id,))
                    def calculate_anciennete(date_in):
                        today = datetime.now()
                        delta = relativedelta(today, date_in)
                        return f"{delta.years} (Ans) {delta.months} (Mois) {delta.days} (Jours)"

                    # Appliquer la fonction de calcul sur la colonne 'Date_In'
                    df['Age'] = df['Birth_Date'].apply(calculate_age)
                    df['Anciennete'] = df['Date_In'].apply(calculate_anciennete)
                    return df
                except mysql.connector.Error as err:
                    st.error(f"Erreur lors de la récupération des effectifs : {err}")
                    return pd.DataFrame()
                finally:
                    conn.close()

            if citrix_id:
                df = get_team_members(citrix_id)

                # Afficher les informations de récapitulatif
                if not df.empty:
                    st.subheader("Récapitulatif des informations de l'utilisateur")
                    
                    st.write(f"**Auteur :** {st.session_state['ID_Citrix_User']}")  # Affiche l'ID Citrix de l'auteur (ID connecté)

                    # Affichage de l'ancien libellé (équipe, compétence ou statut)
                    if selection == "Chang.Equipe" and selected_team:
                        st.write(f"**Ancien Libellé :** {current_team_name}")
                        st.write(f"**Nouveau Libellé :** {selected_team}")
                    elif selection == "Chang.Competence" and selected_competence:
                        st.write(f"**Ancien Libellé :** {current_Competence_name}")
                        st.write(f"**Nouveau Libellé :** {selected_competence}")
                    elif selection == "Chang.Statut" and selected_statut:
                        st.write(f"**Ancien Libellé :** {current_statut_name}")
                        st.write(f"**Nouveau Libellé :** {selected_statut}")
                    elif selection == "Formation" and selected_formation:
                        st.write(f"**Ancien Libellé :** {selected_formation}")
                        
                    st.write(f"**Type d'événement :** {selection}")  # Utilisez `selection` au lieu de `event_type`
                    with st.expander("Voir details"):
                        st.dataframe(df)
                    
                    # Champ de commentaire
                    

                    # Récupérer la date et l'heure
                    event_start_date = st.date_input("Date début événement", min_value=datetime.now())
                    event_start_time = st.time_input("Heure début événement", value=datetime(2025, 2, 6, 0, 0).time())

                    event_end_date = st.date_input("Date fin événement", min_value=datetime.now())
                    event_end_time = st.time_input("Heure fin événement", value=datetime(2025, 2, 6, 0, 0).time())

                    # Combine date et heure
                    event_start_datetime = datetime.combine(event_start_date, event_start_time)
                    event_end_datetime = datetime.combine(event_end_date, event_end_time)

                    # Formater pour afficher la date et l'heure avec les secondes (sans microsecondes)
                    formatted_start_datetime = event_start_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    formatted_end_datetime = event_end_datetime.strftime("%Y-%m-%d %H:%M:%S")

                    # Afficher les informations de date et heure
                    st.write(f"**Date début événement :** {formatted_start_datetime}")
                    st.write(f"**Date fin événement :** {formatted_end_datetime}")
                    commentaire = st.text_area("Commentaire :", height=150)

                else:
                    st.info(f"Aucune information trouvée pour l'ID Citrix {citrix_id}.")
        