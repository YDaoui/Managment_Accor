import streamlit as st
import mysql.connector
from datetime import datetime
from db_utils import get_db_connection, display_logo
import pandas as pd
from contextlib import closing
import os
import smtplib
from email.message import EmailMessage

def convert_hhmmss_to_seconds(time_str):
    """Convertit une durée au format HH:MM:SS en secondes."""
    if not time_str:
        return 0
    try:
        hours, minutes, seconds = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        return 0

def convert_seconds_to_hhmmss(total_seconds):
    """Convertit une durée en secondes en format HH:MM:SS."""
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def fetch_agent_retards(conn, agent_name, start_date, end_date):
    """Récupère les retards non justifiés d'un agent spécifique."""
    with closing(conn.cursor(dictionary=True)) as cursor:
        query = """
            SELECT Date_Retard, Dur_Retard, Justif_Retard, Motif
            FROM retards
            WHERE ID_Citrix = (SELECT ID_Citrix FROM effectifs WHERE Nom_Prenom = %s)
            AND Justif_Retard = 'Non'
            AND Date_Retard BETWEEN %s AND %s
        """
        cursor.execute(query, (agent_name, start_date, end_date))
        retards = cursor.fetchall()
        
        # Convertir la durée en format HH:MM:SS
        for retard in retards:
            duration = retard["Dur_Retard"]  # Objet timedelta
            retard["Dur_Retard"] = convert_seconds_to_hhmmss(duration.total_seconds())
        
        return retards

def update_retard_justification(conn, retard_date, agent_name, justification, commentaire, user_id):
    """Met à jour la justification d'un retard."""
    with closing(conn.cursor()) as cursor:
        update_query = """
            UPDATE retards
            SET Auteur = %s, Justif_Retard = %s, Motif = %s
            WHERE Date_Retard = %s AND ID_Citrix = (SELECT ID_Citrix FROM effectifs WHERE Nom_Prenom = %s)
        """
        cursor.execute(update_query, (user_id, justification, commentaire, retard_date, agent_name))
        conn.commit()

def envoyer_mail(selected_retard, selected_agent, justification, commentaire):
    """Envoie un e-mail de notification de retard."""
    expediteur = "germarocservices@gmail.com"
    destinataire = "germarocservices@gmail.com"
    sujet = "Notification de retard justifié"
    
    contenu = f"""
    Bonjour,

    Je tiens à vous informer que l'agent **{selected_agent}** a fait un retard justifié 
    pour le motif suivant : **{justification}**.

    **Commentaire** : {commentaire}

    Cordialement.
    """

    # Création du message
    msg = EmailMessage()
    msg.set_content(contenu)
    msg["Subject"] = sujet
    msg["From"] = expediteur
    msg["To"] = destinataire

    # Connexion et envoi du mail
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
            serveur.login(expediteur, "Yas23031979$")
            serveur.send_message(msg)
        st.success("E-mail envoyé avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'e-mail : {e}")
        
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

    /* Style pour le titre dans un cadre */
    .custom-title {
        background-image: linear-gradient(to left, #bb8654, #ffffff); /* Dégradé de couleur */
        color: #040233;
        padding: 40px;
        border-radius: 5px;
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        height: 160px; /* Hauteur fixe pour correspondre à l'image */
        display: flex;
        align-items: center; /* Centrer verticalement */
        justify-content: center; /* Centrer horizontalement */
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def retards_Page():
    """Page principale pour la gestion des retards."""
    add_custom_css()
    
    # Afficher le logo de l'entreprise
    col1, col2 = st.columns([1, 5])
    with col1:
        display_logo(os.path.join("Images", "AC1.png"), width=160)
    with col2:
        # Titre dans un cadre avec la couleur des boutons
        st.markdown('<div class="custom-title">Retards Non Justifiés </div>', unsafe_allow_html=True)
    
    # Se connecter à la base de données
    conn = get_db_connection()
    if not conn:
        st.error("Impossible de se connecter à la base de données.")
        return

    # Récupérer l'ID_Citrix de l'utilisateur connecté
    if "ID_Citrix_User" not in st.session_state:
        st.error("Utilisateur non connecté.")
        return
    ID_Citrix_User = st.session_state["ID_Citrix_User"]

    try:
        # Récupérer le Nom_Prenom de l'utilisateur connecté
        with closing(conn.cursor(dictionary=True)) as cursor:
            query = "SELECT Nom_Prenom FROM effectifs WHERE ID_Citrix = %s"
            cursor.execute(query, (ID_Citrix_User,))
            result = cursor.fetchone()

            if result:
                Nom_Prenom_User = result["Nom_Prenom"]
            else:
                st.error("Nom_Prenom de l'utilisateur introuvable.")
                return

        # Colonne 1 : Dates de début et de fin
        with st.container():
            col1, col2 = st.columns([1, 2])
            with col1:
                start_date = st.date_input("Date de début", datetime.now())
                end_date = st.date_input("Date de fin", datetime.now())
                
                if start_date > end_date:
                    st.error("La date de fin ne peut pas être antérieure à la date de début.")
                    return

            # Récupérer les agents de l'équipe qui ont des retards non justifiés
            with closing(conn.cursor(dictionary=True)) as cursor:
                query = """
                    SELECT DISTINCT e.ID_Citrix, e.Nom_Prenom
                    FROM effectifs e
                    JOIN retards r ON e.ID_Citrix = r.ID_Citrix
                    WHERE e.Statut = 'Agent' 
                    AND r.Justif_Retard = 'Non'
                    AND r.Date_Retard BETWEEN %s AND %s
                    AND e.Team = %s
                """
                cursor.execute(query, (start_date, end_date, Nom_Prenom_User))
                agents = cursor.fetchall()

            if agents:
                all_retards = []
                for agent in agents:
                    retards_agent = fetch_agent_retards(conn, agent["Nom_Prenom"], start_date, end_date)
                    for retard in retards_agent:
                        all_retards.append({
                            "Nom_Prenom": agent["Nom_Prenom"],
                            "Date_Retard": retard["Date_Retard"],
                            "Durée_Retard": retard["Dur_Retard"],
                        })

                # Afficher le tableau des retards non justifiés dans la première colonne
                with col1:
                    # Calculer la somme totale des durées
                    total_seconds = sum(convert_hhmmss_to_seconds(retard["Durée_Retard"]) for retard in all_retards)
                    total_duration = convert_seconds_to_hhmmss(total_seconds)
                    st.subheader(f"Total cumulé des retards : {total_duration}")
                    retards_df = pd.DataFrame(all_retards)
                    st.table(retards_df)

                # Interaction avec un agent spécifique dans la deuxième colonne
                with col2:
                    selected_agent = st.selectbox("Sélectionnez un agent pour voir ses retards non justifiés", [agent["Nom_Prenom"] for agent in agents])
                    if selected_agent:
                        agent_retards = fetch_agent_retards(conn, selected_agent, start_date, end_date)
                    
                        if agent_retards:
                            st.subheader(f"Retards Non Justifiés de {selected_agent}")
                            agent_retards_df = pd.DataFrame(agent_retards)
                            st.table(agent_retards_df)
                            
                            # Calculer la somme totale des durées pour cet agent
                            total_seconds_agent = sum(convert_hhmmss_to_seconds(retard["Dur_Retard"]) for retard in agent_retards)
                            total_duration_agent = convert_seconds_to_hhmmss(total_seconds_agent)
                            st.subheader(f"Total cumulé des retards pour {selected_agent} : {total_duration_agent}")
                                    
                        else:
                            st.info("Aucun retard trouvé pour cet agent dans la période sélectionnée.")
                            
                        # Sélectionner un retard à justifier avec date et durée
                        retard_options = [f"{retard['Date_Retard']} {retard['Dur_Retard']}" for retard in agent_retards]
                        selected_retard = st.selectbox("Sélectionnez un retard à justifier", retard_options)
                        
                        # Extraire la date et la durée du retard sélectionné
                        selected_retard_date = selected_retard.split()[0]
                        selected_retard_duration = selected_retard.split()[1]
                        
                        st.subheader(f"Durée de retard : {selected_retard_duration}")
                        justification = st.selectbox("Justification", ["Oui", "Non"])
                        commentaire = st.text_area("Commentaire :", height=100)

                        # Boutons pour justifier le retard
                        col1, col2, col3 = st.columns([4, 4, 4])
                        with col1:
                            if st.button("**Par mail**", use_container_width=True):
                                envoyer_mail(selected_retard_date, selected_agent, justification, commentaire)
                        with col2:
                            if st.button("**Enregistrer**", use_container_width=True):
                                update_retard_justification(conn, selected_retard_date, selected_agent, justification, commentaire, ID_Citrix_User)
                                st.success(f"Retard du {selected_retard_date} mis à jour avec succès!")
                        with col3:
                            if st.button("**Annuler**", use_container_width=True):
                                st.info("Aucune modification n'a été effectuée.")

            else:
                st.info("Aucun retard non justifié trouvé pour votre équipe.")

    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la récupération des données : {err}")

# Exécution de la page
if __name__ == "__main__":
    retards_Page()
