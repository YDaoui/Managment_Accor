import streamlit as st
import mysql.connector
from PIL import Image
import os
from datetime import datetime
import pandas as pd
from streamlit_option_menu import option_menu
from contextlib import closing
from datetime import datetime

# Configuration de la base de données
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD", "YDaoui2303"),
            database="Accorhotels_cube_DB"
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Erreur de connexion à la base de données: {err}")
        return None

# Vérification des informations d'identification (sans hachage)
def authenticate(ID_Citrix_User, password):
    
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with closing(conn.cursor()) as cursor:
            query = "SELECT Role, Password FROM users WHERE Login = %s"
            cursor.execute(query, (ID_Citrix_User,))
            result = cursor.fetchone()
            if result:
                stored_password = result[1]
                if stored_password == password:  # Comparaison simple des mots de passe
                    return result[0]
            return None
    except mysql.connector.Error as err:
        st.error(f"Erreur d'authentification: {err}")
        return None
    finally:
        conn.close()

# Récupérer le nom et le prénom de l'utilisateur
def get_user_name(ID_Citrix_User):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            query = "SELECT Nom_Prenom FROM effectifs WHERE ID_Citrix = %s"
            cursor.execute(query, (ID_Citrix_User,))
            result = cursor.fetchone()
            return result["Nom_Prenom"] if result else "Utilisateur"
    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la récupération du nom et prénom : {err}")
        return "Utilisateur"
    finally:
        conn.close()

# Page de connexion
def login_page():
    col1, col2 = st.columns([1, 2])

    with col1:
        display_logo(os.path.join("Images", "AC.png"), width=280)

    with col2:
    
        st.header("Page de connexion")
        ID_Citrix_User = st.text_input("ID Citrix")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            role = authenticate(ID_Citrix_User, password)
            if role:
                st.session_state["authenticated"] = True
                st.session_state["Role"] = role
                st.session_state["ID_Citrix_User"] = ID_Citrix_User
                st.session_state["Nom_Prenom"] = get_user_name(ID_Citrix_User)
                st.success("Connexion réussie !")
                st.rerun()  # Recharger la page pour afficher le menu
            else:
                st.error("Échec de l'authentification. Veuillez vérifier vos informations d'identification.")

# Fonction pour afficher un logo
def display_logo(image_path, width):
    try:
        img = Image.open(image_path)
        st.image(img, width=width)
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image : {e}")

# Fonction pour colorer les cellules
def color_cells(val):
    if val == "Pause_Dej":
        return "background-color: #a88054"  # Rouge clair pour Pause_Dej
    elif val == "G2P":
        return "background-color: #f1c579"  # Bleu clair pour G2P
    return ""  # Pas de style pour les autres valeurs

# Page pour les agents
def agent_page():
    col1, col2 = st.columns([1, 9])

    with col1:
        display_logo(os.path.join("Images", "AC.png"), width=120)

    with col2:
        st.header("Planning")

    # Récupérer l'ID Citrix de l'agent connecté
    ID_Citrix_User = st.session_state["ID_Citrix_User"]

    # Connexion à la base de données
    conn = get_db_connection()
    if not conn:
        st.error("Impossible de se connecter à la base de données.")
        return

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            # Requête pour récupérer le planning de l'agent
            query = """
            SELECT Date_Planning, 7_00, 7_30, 8_00, 8_30, 9_00, 9_30, 
                   10_00, 10_30, 11_00, 11_30, 12_00, 
                   12_30, 13_00, 13_30, 14_00, 14_30, 
                   15_00, 15_30, 16_00, 16_30, 17_00, 
                   17_30, 18_00, 18_30, 19_00
            FROM Plannings
            WHERE ID_Citrix = %s
            ORDER BY Date_Planning DESC
            """
            cursor.execute(query, (ID_Citrix_User,))
            planning_data = cursor.fetchall()

            if planning_data:
                # Convertir les données en DataFrame Pandas
                df = pd.DataFrame(planning_data)

                # Appliquer le style aux cellules
                styled_df = df.style.applymap(color_cells)

                # Afficher le tableau du planning avec les couleurs
                st.write("Voici votre planning :")
                st.write(styled_df.to_html(), unsafe_allow_html=True)
            else:
                st.info("Aucun planning trouvé pour cet ID Citrix.")
    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la récupération du planning : {err}")
    finally:
        conn.close()

# Page globale
def global_page():
    display_logo(os.path.join("Images", "th.jpeg"), width=120)
    st.header("Nombre d'utilisateurs par compétence")

# Page des événements
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
        def get_team_members(citrix_id):
            conn = get_db_connection()
            if not conn:
                return pd.DataFrame()

            try:
                query = """
                    SELECT Nom_Prenom, UM, Team, Competence, Statut, Date_In
                    FROM effectifs WHERE ID_Citrix = %s
                """
                df = pd.read_sql(query, conn, params=(citrix_id,))
                return df
            except mysql.connector.Error as err:
                st.error(f"Erreur lors de la récupération des effectifs : {err}")
                return pd.DataFrame()
            finally:
                conn.close()

        if citrix_id:
            df = get_team_members(citrix_id)

# Récupérer la date et l'heure comme avant
            from datetime import datetime

# Récupérer la date et l'heure comme avant
            event_start_date = st.date_input("Date début événement", min_value=datetime.now())
            event_start_time = st.time_input("Heure début événement", value=datetime(2025, 2, 6, 0, 0).time())

            event_end_date = st.date_input("Date fin événement", min_value=datetime.now())
            #event_end_time = st.time_input("Heure fin événement", value=datetime.now().time())
            event_end_time = st.time_input("Heure fin événement", value=datetime(2025, 2, 6, 0, 0).time())
            # Combine date et heure
            event_start_datetime = datetime.combine(event_start_date, event_start_time)
            event_end_datetime = datetime.combine(event_end_date, event_end_time)

            # Formater pour afficher la date et l'heure avec les secondes (sans microsecondes)
            formatted_start_datetime = event_start_datetime.strftime("%Y-%m-%d %H:%M:%S")
            formatted_end_datetime = event_end_datetime.strftime("%Y-%m-%d %H:%M:%S")

            # Afficher les informations
            #st.write(f"**Date début événement :** {formatted_start_datetime}")  # Affiche la date et l'heure
            #st.write(f"**Date fin événement :** {formatted_end_datetime}")  # Affiche la date et l'heure

            event_type = selection

            # Afficher les informations de récapitulatif
            if not df.empty:
                st.subheader("Récapitulatif des informations de l'utilisateur")
                
                st.write(f"**Auteur :** {st.session_state['ID_Citrix_User']}")  # Affiche l'ID Citrix de l'auteur (ID connecté)

                # Affichage de l'ancien libellé (équipe, compétence ou statut)
                if selection == "Chang.Equipe" and selected_team:
                    st.write(f"**Ancien Libellé :** {current_team_name}")
                    st.write(f"**Nouveau Libellé :** {selected_team}")
                    st.write(f"**Date début événement :** {formatted_start_datetime}")  # Affiche la date de début avec l'heure
                    st.write(f"**Date fin événement :** {formatted_end_datetime}") 
                elif selection == "Chang.Competence" and selected_competence:
                    st.write(f"**Ancien Libellé :** {current_Competence_name}")
                    st.write(f"**Nouveau Libellé :** {selected_competence}")
                    st.write(f"**Date début événement :** {formatted_start_datetime}")  # Affiche la date de début avec l'heure
                    st.write(f"**Date fin événement :** {formatted_end_datetime}") 
                elif selection == "Chang.Statut" and selected_statut:
                    st.write(f"**Ancien Libellé :** {current_statut_name}")
                    st.write(f"**Nouveau Libellé :** {selected_statut}")
                    st.write(f"**Date début événement :** {formatted_start_datetime}")  # Affiche la date de début avec l'heure
                    st.write(f"**Date fin événement :** {formatted_end_datetime}") 
                elif selection == "Formation" and selected_formation:
                    st.write(f"**Ancien Libellé :** {selected_formation}")
                    st.write(f"**Date début événement :** {formatted_start_datetime}")  # Affiche la date de début avec l'heure
                    st.write(f"**Date fin événement :** {formatted_end_datetime}") 

                st.write(f"**Type d'événement :** {event_type}")
                st.dataframe(df)
                st.text_input("Commentaire :")  # Affiche le tableau des utilisateurs
                 # Affiche la date de fin avec l'heure

            else:
                st.info(f"Aucune information trouvée pour l'ID Citrix {citrix_id}.")

# Fonction principale pour démarrer l'application Streamlit avec un menu
def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "Role" not in st.session_state:
        st.session_state["Role"] = None
    if "ID_Citrix_User" not in st.session_state:
        st.session_state["ID_Citrix_User"] = None
    if "Nom_Prenom" not in st.session_state:
        st.session_state["Nom_Prenom"] = "Utilisateur"

    if not st.session_state["authenticated"]:
        login_page()
    else:
        role = st.session_state["Role"]
        NomP = st.session_state['Nom_Prenom']
        
        # Mise à jour de la sidebar
        if role == "Agent":
            with st.sidebar:
                
                st.markdown(f"<h2 style='color: white;'>Bienvenu, <strong>{NomP}</strong>!</h3>", unsafe_allow_html=True)

 # Affichage du nom et prénom de l'utilisateur
                selected = option_menu(
                    f"Menu {st.session_state['Nom_Prenom']}",  # Inclure le Nom_Prenom ici
                    ["Planning", "Congés"],
                    icons=["calendar", "Home"],
                    menu_icon="menu",
                    default_index=0,
                    orientation="vertical",
                    styles={
                        "container": {"background-color": "#040233"},
                        "icon": {"color": "white"},
                        "nav-link": {
                            "font-size": "16px",
                            "text-align": "left",
                            "margin": "0px",
                            "color": "white",
                        },
                        "nav-link-selected": {"background-color": "#ebb26d"},
                    },
                )
            if selected == "Planning":
                agent_page()
        else:
            with st.sidebar:
                
                st.markdown(f"<h3 style='color: white;'>Bienvenu, <strong>{NomP}</strong>!</h3>", unsafe_allow_html=True)
  # Affichage du nom et prénom de l'utilisateur
                selected = option_menu(
                    f"Menu {st.session_state['Nom_Prenom']}",
                    #f"Menu {NomP}",
                    ["Global", "Retards", "Equipe", "Evenements"],
                    icons=["house", "clock", "calendar-event", "calendar-event"],
                    menu_icon="menu",
                    default_index=0,
                    orientation="vertical",
                    styles={
                        "container": {"background-color": "#040233"},
                        "icon": {"color": "white"},
                        "nav-link": {
                            "font-size": "16px",
                            "text-align": "left",
                            "margin": "0px",
                            "color": "white",
                        },
                        "nav-link-selected": {"background-color": "#ebb26d"},
                    },
                )

            if selected == "Global":
                global_page()
            elif selected == "Retards":
                st.header("Page des Retards")
            elif selected == "Evenements":
                Evenement_page()
            elif selected == "Equipe":
                st.header("Page Equipe")

if __name__ == "__main__":
    main()