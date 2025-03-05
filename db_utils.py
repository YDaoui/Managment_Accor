import streamlit as st
import mysql.connector
import os
from PIL import Image
from datetime import datetime
from dateutil.relativedelta import relativedelta
from contextlib import closing


def calculate_age(birth_date):
            today = datetime.now()
            delta = relativedelta(today, birth_date)
            return f"{delta.years} (Ans) "

def calculate_anciennete(date_in):
                        today = datetime.now()
                        delta = relativedelta(today, date_in)
                        return f"{delta.years} (Ans) {delta.months} (Mois) {delta.days} (Jours)"



def color_cells(val):
    if val == "Pause_Dej":
        return "background-color: #ffcb84"  # Rouge clair pour Pause_Dej
    elif val == "G2P":
        return "background-color: #5ac2db"  # Bleu clair pour G2P
    return ""
# Connexion à la base de données
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="10.10.@@@@@",
            user="********",
            password=os.getenv("DB_PASSWORD", "******"),
            database="@@@@@@@@@@@@@@@"
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Erreur de connexion à la base de données: {err}")
        return None

# Authentification de l'utilisateur
def authenticate(login, password):
    conn = get_db_connection()
    if not conn:
        st.error("Erreur de connexion à la base de données.")
        return False, None

    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            # Requête pour vérifier le login et le mot de passe
            query = "SELECT ID_Citrix, Password FROM users WHERE Login = %s"
            cursor.execute(query, (login,))
            result = cursor.fetchone()

            if result:
                stored_password = result["Password"]
                if stored_password == password:  # Comparaison simple des mots de passe
                    ID_Citrix = result["ID_Citrix"]
                    
                    # Mettre à jour la session avec l'ID_Citrix
                    st.session_state["ID_Citrix"] = ID_Citrix
                    st.session_state["Nom_Prenom"] =  get_user_status(ID_Citrix)  # Récupérer le nom
                    st.session_state["Statut"] = get_user_status(ID_Citrix)  # Récupérer le statut
                    
                    #st.write(f"ID Citrix récupéré : {ID_Citrix}")  # Log pour vérifier
                    return True, ID_Citrix
            return False, None
    except mysql.connector.Error as err:
        st.error(f"Erreur lors de l'authentification : {err}")
        return False, None
    finally:
        conn.close()

# Récupérer le statut de l'utilisateur
def get_user_status(ID_Citrix):
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = "SELECT Statut FROM effectifs WHERE ID_Citrix = %s"
            cursor.execute(query, (ID_Citrix,))
            result = cursor.fetchone()
            return result["Statut"] if result else None
            return result["Nom_prenom"] if result else "Utilisateur non trouvé"
    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la récupération du statut : {err}")
        return None
    finally:
        conn.close()


def get_user_name(ID_Citrix):
    conn = get_db_connection()
    if not conn:
        return "Utilisateur"
    
    try:
        with closing(conn.cursor(dictionary=True)) as cursor:
            query = "SELECT Nom_prenom FROM effectifs WHERE ID_Citrix = %s"
            cursor.execute(query, (ID_Citrix,))
            result = cursor.fetchone()
            return result["Nom_prenom"] if result else "Utilisateur non trouvé"
    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la récupération du nom et prénom : {err}")
        return "Erreur lors de la récupération"
    finally:
        conn.close()


# Afficher le logo
def display_logo(image_path, width):
    try:
        img = Image.open(image_path)
        st.image(img, width=width)
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image : {e}")

# Page de connexion

def login_page():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        col1, col2 = st.columns([1, 2])

        with col1:
            display_logo(os.path.join("Images", "AC.png"), width=280)

        with col2:
            st.subheader("Page de connexion")
            login = st.text_input("Nom d'utilisateur : ")
            password = st.text_input("Mot de passe :", type="password")

            if st.button("Se connecter"):
                is_authenticated, ID_Citrix_User = authenticate(login, password)
                if is_authenticated:
                    statut = get_user_status(ID_Citrix_User)
                    st.session_state["authenticated"] = True
                    st.session_state["Statut"] = statut
                    st.session_state["ID_Citrix"] = ID_Citrix_User
                    st.session_state["Nom_Prenom"] = get_user_name(ID_Citrix_User)
                    st.success(f"Connexion réussie en tant que {statut} !")
                    st.rerun()  # Recharger la page après authentification
                else:
                    st.error("Échec de l'authentification. Veuillez vérifier vos informations d'identification.")
