import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from contextlib import closing
from db_utils import get_user_name, display_logo, authenticate, get_user_status, login_page,get_db_connection



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
# Fonction pour se connecter à MySQL
def get_mysql_connection():
    try:
        st.info("Tentative de connexion à la base de données MySQL...")
        conn = mysql.connector.connect(
            host="localhost",  # Assurez-vous que l'hôte est correct
            user="root",       # L'utilisateur MySQL
            password=os.getenv("DB_PASSWORD", "YDaoui2303"),  # Mot de passe de la base de données
            database="accorhotels_cube_db"  # Nom de la base de données
        )
        if conn.is_connected():
            st.info("Connexion réussie à la base de données MySQL.")
            return conn
        else:
            st.error("Échec de la connexion à la base de données.")
            return None
    except mysql.connector.Error as err:
        st.error(f"Erreur de connexion à la base de données: {err}")
        return None

# Fonction pour récupérer les données de la table Retards
def get_retards_data_from_mysql():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Retards")
            db_data = cursor.fetchall()
            columns = ['ID_Retards', 'ID_Citrix', 'Date_Retard', 'Auteur', 'Dur_Retard', 'Justif_Retard', 'Date_Sais_Retard', 'Motif']
            df_mysql = pd.DataFrame(db_data, columns=columns)
            return df_mysql
            add_custom_css()
        except Error as e:
            st.error(f"Erreur lors de la récupération des données de la table Retards: {e}")
            return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur
        finally:
            if conn.is_connected():
                pd.DataFrame()
                cursor.close()
                conn.close()
    else:
        return pd.DataFrame()  # Retourne un DataFrame vide si la connexion échoue

# Fonction pour insérer les données dans la base de données
def insert_data_to_mysql(df_new):
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Insérer les nouvelles données dans la table Retards
        for _, row in df_new.iterrows():
            date_retard = row['Date_Retard'].strftime('%Y-%m-%d') if isinstance(row['Date_Retard'], pd.Timestamp) else row['Date_Retard']
            date_sais_retard = row['Date_Sais_Retard'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(row['Date_Sais_Retard'], pd.Timestamp) else row['Date_Sais_Retard']
            # Convertir Dur_Retard en format '%H:%M:%S'
            dur_retard = row['Dur_Retard'].strftime('%H:%M:%S') if isinstance(row['Dur_Retard'], pd.Timedelta) else row['Dur_Retard']

            cursor.execute("""
                INSERT INTO Retards (ID_Citrix, Date_Retard, Auteur, Dur_Retard, Justif_Retard, Date_Sais_Retard, Motif)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row['ID_Citrix'],
                date_retard,
                row['Auteur'],
                dur_retard,
                row['Justif_Retard'],
                date_sais_retard,
                row['Motif']
            ))

        conn.commit()  # Valider les modifications
        return True
    except Error as e:
        st.error(f"Erreur lors de l'insertion dans MySQL: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Fonction principale de l'application Streamlit
def main():
    st.title("Importation de Retards vers la Base de Données MySQL")

    # Connexion à MySQL et récupération des données de la table Retards
    st.info("Récupération des données de la base de données MySQL...")
    df_mysql = get_retards_data_from_mysql()

    if df_mysql.empty:
        st.warning("Aucune donnée trouvée dans la table Retards ou échec de la connexion à MySQL.")
    else:
        st.write("Voici les données existantes dans la base de données :")
        st.dataframe(df_mysql)  # Afficher les données existantes dans la table Retards

    # Charger le fichier Excel
    uploaded_file = st.file_uploader("Choisir un fichier Excel", type=["xlsx"])

    if uploaded_file is not None:
        st.info("Le fichier a été chargé avec succès. Traitement en cours...")

        # Charger la feuille Excel dans un DataFrame
        try:
            df_excel = pd.read_excel(uploaded_file, sheet_name="Retards")
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier Excel: {e}")
            return

        # Convertir la colonne Dur_Retard en timedelta
        df_excel['Dur_Retard'] = pd.to_timedelta(df_excel['Dur_Retard'], errors='coerce')

        # Vérification du contenu du DataFrame
        st.write("Voici les données du fichier Excel chargé:")
        st.dataframe(df_excel)  # Afficher un aperçu des données

        # Ajouter un bouton pour exporter les données
        if st.button("Exporter vers la base de données"):
            if not df_mysql.empty:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    # Filtrer les nouvelles lignes à insérer
                    cursor.execute("SELECT ID_Retards FROM Retards")
                    existing_ids = [row[0] for row in cursor.fetchall()]
                    
                    st.info("Filtrage des nouvelles lignes à insérer...")
                    df_new = df_excel[~df_excel['ID_Retards'].isin(existing_ids)]
                    st.write(f"{len(df_new)} nouvelles lignes à insérer.")

                    # Insertion des nouvelles lignes dans MySQL
                    if insert_data_to_mysql(df_new):
                        st.success(f"{len(df_new)} nouvelles lignes ont été insérées dans la base de données.")
                    else:
                        st.error("Une erreur est survenue lors de l'exportation des données.")
                except Error as e:
                    st.error(f"Erreur lors de la connexion à la base de données MySQL: {e}")
                finally:
                    if conn.is_connected():
                        cursor.close()
                        conn.close()
            else:
                st.error("Connexion à la base de données échouée ou aucune donnée à afficher dans la table Retards.")

# Exécution de l'application Streamlit
if __name__ == "__main__":
    main()