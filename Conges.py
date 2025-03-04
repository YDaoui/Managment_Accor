import streamlit as st
import mysql.connector
from datetime import datetime
from db_utils import get_db_connection, get_user_name, display_logo, color_cells,login_page,authenticate,calculate_age,calculate_anciennete
from contextlib import closing
import os
from datetime import timedelta
import pandas as pd

# Définition de la fonction pour la page des congés
def Conge_page():
    # Première ligne avec l'image et le titre
    col1, col2 = st.columns([1, 9])

    with col1:
        display_logo(os.path.join("Images", "AC.png"), width=120)

    with col2:
        st.header("Congés")

    # Vérifier si la clé "ID_Citrix_User" est présente dans session_state
    if "ID_Citrix_User" not in st.session_state:
        st.error("L'utilisateur n'est pas connecté ou la clé 'ID_Citrix_User' n'a pas été initialisée.")
        return

    # Récupérer l'ID Citrix de l'agent connecté
    ID_Citrix_User = st.session_state["ID_Citrix_User"]

    # Connexion à la base de données
    conn = get_db_connection()
    if not conn:
        st.error("Impossible de se connecter à la base de données.")
        return

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            # Requête pour récupérer les informations de l'agent
            query = """
                SELECT Nom_Prenom, UM, Team, Competence, Gender, Birth_Date, Date_In, Solde_Conge
                FROM effectifs WHERE ID_Citrix = %s
            """
            cursor.execute(query, (ID_Citrix_User,))  # Passer (ID_Citrix_User,) comme tuple
            data_conges = cursor.fetchall()

            if data_conges:
                # Récupérer la première ligne des résultats
                agent_data = data_conges[0]

                # Calculer l'âge et l'ancienneté
                age = calculate_age(agent_data['Birth_Date'])
                anciennete = calculate_anciennete(agent_data['Date_In'])

                # Afficher les informations dans un cadre
                with st.expander("Détails de l'Agent", expanded=True):
                    
                    st.markdown(f"**Nom et Prénom :** {agent_data['Nom_Prenom']}")
                    
                    st.markdown(f"**Équipe :** {agent_data['Team']}")
                    st.markdown(f"**UM :** {agent_data['UM']}")
                    st.markdown(f"**Compétence :** {agent_data['Competence']}")
                    st.markdown(f"**Genre :** {agent_data['Gender']}")
                    st.markdown(f"**Âge :** {age}")
                    st.markdown(f"**Ancienneté :** {anciennete}")
                    st.markdown(f"**Solde de Congé :** {round(agent_data['Solde_Conge'], 0)} jours")
            else:
                st.warning("Aucune donnée de congé disponible pour cet agent.")

    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la récupération des congés : {err}")

    finally:
        conn.close()  # La connexion sera fermée, qu'il y ait une erreur ou non

    # Partie de gestion des congés
    col1, col2 , col3 , col4= st.columns([3, 3, 1, 8])

    with col1:
        # Liste des types de congés
        options = ["Congé payé (CP)", "Congé maladie", "Congé maternité", "Congé paternité", 
                   "Congé d'adoption", "Congé pour événements familiaux", "Congé sabbatique", 
                   "Congé de solidarité familiale", "Congé de formation", "Congé pour création d'entreprise", 
                   "Congé pour bilan de compétences", "Congé de solidarité nationale", 
                   "Congé de longue maladie (CLM)", "Congé de longue durée (CLD)", 
                   "Congé de proche aidant"]

        # Récupérer et afficher le solde de congé
        solde_congé = f"Solde de Congé restant : {round(agent_data['Solde_Conge'], 0)} jours"
        st.markdown(f"**Solde de Congé restant :** {round(agent_data['Solde_Conge'], 0)} jours")
        #st.text_area("Solde de Congé restant", value=solde_congé, height=68, disabled=True)

        # Vérifier si les valeurs sont déjà présentes dans session_state, sinon les initialiser
        if 'selection' not in st.session_state:
            st.session_state.selection = options[0]  # Valeur par défaut du type de congé
        if 'Date_Debut_Conge' not in st.session_state:
            st.session_state.Date_Debut_Conge = datetime.now().date()
        if 'Date_Fin_Conge' not in st.session_state:
            st.session_state.Date_Fin_Conge = datetime.now().date()
        if 'commentaire' not in st.session_state:
            st.session_state.commentaire = ""

        # Sélection du type de congé
        selection = st.selectbox("Type de Congé :", options, index=options.index(st.session_state.selection))

        # Date de demande de congé (désactivée pour ne pas être modifiée)
        

        # Champ commentaire (plus grand)
        commentaire = st.text_area("Commentaire :", height=150, value=st.session_state.commentaire)
    
    with col2:
        #st.header("Details Enregistrement :")
        
        Date_Dde_Conge = datetime.now().date()
        st.markdown(f"Date de congé :    {Date_Dde_Conge}")


        #Date_Dde_Conge = st.date_input("Date Demande de Congé", min_value=datetime.now(), disabled=True)

        # Date de début de congé
        Date_Debut_Conge = st.date_input("Date début Congé", min_value=datetime.now(), value=st.session_state.Date_Debut_Conge)

        # Date de fin de congé
        Date_Fin_Conge = st.date_input("Date fin Congé", min_value=datetime.now(), value=st.session_state.Date_Fin_Conge)

        # Calculer le nombre de jours entre la date de début et la date de fin du congé
        if Date_Debut_Conge and Date_Fin_Conge:
            # Initialisation du nombre de jours de congé à 0
            nombre_jours_conge = 0

            # Parcours de chaque jour dans la période
            current_date = Date_Debut_Conge
            while current_date <= Date_Fin_Conge:
                # Vérifier si le jour est un lundi (0) à vendredi (4)
                if current_date.weekday() < 5:  # 0 = lundi, 1 = mardi, ..., 4 = vendredi
                    nombre_jours_conge += 1
                # Passer au jour suivant
                current_date += timedelta(days=1)

            # Vérifier si le nombre de jours de congé dépasse le solde de congé
            if nombre_jours_conge > round(agent_data['Solde_Conge'], 1):
                st.error("**Solde insuffisant** : Vous ne pouvez pas prendre plus de jours que votre solde de congé.")

    # Créer un DataFrame avec les informations de la demande de congé
        

        data = {
        "Champ": ["Type de Congé", "Date Début Congé", "Date Fin Congé", "Commentaire", "Nombre de jours", "Auteur"],
        "Valeur": [selection, Date_Debut_Conge, Date_Fin_Conge, commentaire, nombre_jours_conge, ID_Citrix_User]
        }

        df = pd.DataFrame(data)

    # Afficher le DataFrame sous forme de tableau
        
    with col3:
        
            st.header("")
    with col4:
            st.header("Historique des Congés :")
            # Connexion à la base de données pour récupérer les congés de l'agent
            conn = get_db_connection()
            if not conn:
                st.error("Impossible de se connecter à la base de données.")
            else:
                try:
                    with closing(conn.cursor(dictionary=True)) as cursor:
                        # Requête pour récupérer les congés de l'agent connecté
                        query = """
                            SELECT ID_Conge, Type_conge, Date_Dde_Conge, Date_Debut_Conge, Date_Fin_Conge, Commentaire_Conge
                            FROM conges
                            WHERE ID_Citrix = %s
                            ORDER BY Date_Dde_Conge DESC
                        """
                        cursor.execute(query, (ID_Citrix_User,))
                        conges_agent = cursor.fetchall()

                        if conges_agent:
                            # Afficher les congés dans un tableau
                            st.dataframe(conges_agent)
                            st.dataframe(df, hide_index=True, use_container_width=True)
                        else:
                            st.info("Aucun congé enregistré pour cet agent.")
                except mysql.connector.Error as err:
                    st.error(f"Erreur lors de la récupération des congés : {err}")
                finally:
                    conn.close()

    # Ajouter les boutons Enregistrer et Annuler
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("**Enregistrer**",use_container_width=True):
            # Insertion dans la table de congé
            try:
                conn = get_db_connection()
                with closing(conn.cursor()) as cursor:
                    # Requête d'insertion
                    query = """
                        INSERT INTO conges (ID_Citrix, Auteur, Type_conge, Date_Dde_Conge, Date_Debut_Conge, Date_Fin_Conge, Commentaire_Conge)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (
                        ID_Citrix_User,  # ID_Citrix
                        ID_Citrix_User,  # Auteur
                        selection,  # Type de Congé
                        Date_Dde_Conge,  # Date de Demande
                        Date_Debut_Conge,  # Date de Début
                        Date_Fin_Conge,  # Date de Fin
                        commentaire  # Commentaire
                    ))
                    conn.commit()  # Enregistrer dans la base de données
                    st.success("Votre demande de congé a été enregistrée avec succès.")
            except mysql.connector.Error as err:
                st.error(f"Erreur lors de l'enregistrement de la demande : {err}")
            finally:
                if conn:
                    conn.close()

    with col2:
        if st.button("**Annuler**",use_container_width=True):
            # Réinitialiser tous les champs sauf les dates, type de congé et solde
            st.session_state.selection = options[0]  # Garder le premier type de congé
            st.session_state.Date_Debut_Conge = datetime.now().date()  # Garder la date du jour
            st.session_state.Date_Fin_Conge = datetime.now().date()  # Garder la date du jour
            st.session_state.commentaire = ""  # Réinitialiser le commentaire
            st.rerun()  # Réinitialiser l'interface
