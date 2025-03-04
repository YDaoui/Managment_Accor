import streamlit as st
import mysql.connector
from PIL import Image
import os

from datetime import datetime
import pandas as pd
from streamlit_option_menu import option_menu
from contextlib import closing
#from db_utils import get_db_connection, get_user_name, 
from db_utils import get_db_connection,display_logo, color_cells,authenticate



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


def Planning_page():
    add_custom_css()
    col1, col2 ,col3= st.columns([2, 3,  9])

    with col1:
        display_logo(os.path.join("Images", "AC.png"), width=120)

    with col2:
        st.header("Planning", anchor=False)
        st.write(f"<b><span style='color:#040233;'>Selecteurs de période de votre planning  :</span></b>", unsafe_allow_html=True)
       # st.write(styled_df.to_html(), unsafe_allow_html=True)
    with col3:
        start_date = st.date_input("Date de début", datetime.now())
        end_date = st.date_input("Date de fin", datetime.now())

    if start_date and end_date and start_date <= end_date:
        # Récupérer l'ID Citrix de l'agent connecté
        ID_Citrix_User = st.session_state["ID_Citrix_User"]

        # Connexion à la base de données
        conn = get_db_connection()
        if not conn:
            st.error("Impossible de se connecter à la base de données.")
            return

        try:
            with closing(conn.cursor(dictionary=True)) as cursor:
                # Requête pour récupérer le planning de l'agent entre les dates sélectionnées
                query = """
                SELECT Date_Planning, 7_00, 7_30, 8_00, 8_30, 9_00, 9_30, 
                       10_00, 10_30, 11_00, 11_30, 12_00, 
                       12_30, 13_00, 13_30, 14_00, 14_30, 
                       15_00, 15_30, 16_00, 16_30, 17_00, 
                       17_30, 18_00, 18_30, 19_00
                FROM Plannings
                WHERE ID_Citrix = %s AND Date_Planning BETWEEN %s AND %s
                ORDER BY Date_Planning DESC
                """
                cursor.execute(query, (ID_Citrix_User, start_date, end_date))
                planning_data = cursor.fetchall()

                if planning_data:
                    # Convertir les données en DataFrame Pandas
                    df = pd.DataFrame(planning_data)
                    df['Date_Planning'] = pd.to_datetime(df['Date_Planning'])
                    df['Jour'] = df['Date_Planning'].dt.strftime('%A')  # Jour de la semaine
                    df['Semaine'] = df['Date_Planning'].dt.strftime('S%U')  # Numéro de la semaine
                    df['Nbr Heure'] = df.iloc[:, 1:].apply(lambda row: (row == 'G2P').sum() / 2, axis=1).astype(int)
                    total_hours = df['Nbr Heure'].sum()
                    def get_first_shift(row):
                        for col in df.columns[1:]:
                            if row[col] == 'G2P':
                                return col
                        return None  # Si aucun G2P n'est trouvé

                    df['Shift'] = df.apply(get_first_shift, axis=1)
                    # Réorganiser les colonnes
                    columns_order = ['Semaine', 'Jour', 'Shift', 
                                     '7_00', '7_30', '8_00', '8_30', '9_00', '9_30', 
                                     '10_00', '10_30', '11_00', '11_30', '12_00', 
                                     '12_30', '13_00', '13_30', '14_00', '14_30', 
                                     '15_00', '15_30', '16_00', '16_30', '17_00', 
                                     '17_30', '18_00', '18_30', '19_00', 'Nbr Heure']
                    df = df[columns_order]

                    # Appliquer le style aux cellules
                    styled_df = df.style.applymap(color_cells)

                    # Afficher le tableau du planning avec les couleurs
                    
                    st.write(f"<b><span style='color:#040233;'>Voici votre planning (Total heures: {total_hours}) :</span></b>", unsafe_allow_html=True)
                    st.write(styled_df.to_html(), unsafe_allow_html=True)
                else:
                    st.info("Aucun planning trouvé pour cet ID Citrix dans la période sélectionnée.")
        except mysql.connector.Error as err:
            st.error(f"Erreur lors de la récupération du planning : {err}")
        finally:
            conn.close()
    else:
        st.info("Veuillez sélectionner une date de début et une date de fin pour afficher le planning.")

# Appel de la fonction Planning_page
if __name__ == "__main__":
    Planning_page()
