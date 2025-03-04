import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from db_utils import get_db_connection, display_logo, calculate_age, calculate_anciennete
from datetime import datetime

def add_custom_css():
    custom_css = """
  <style>
    footer {visibility: hidden;}

    body, .stApp, .main {
        background-color: #FFFFFF !important;
    }

    /* Texte en gras avec couleur #1c1c4c */
    * {
        font-weight: bold !important;
        color: #1c1c4c !important;
    }

    /* Boutons */
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

    /* Champs de sélection */
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

    /* Barre latérale */
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

def get_effectifs_data():
    try:
        conn = get_db_connection()
        if not conn:
            return None, None

        query_effectifs = "SELECT * FROM effectifs WHERE Statut = 'agent';"
        query_ventes = "SELECT * FROM ventes;"

        effectifs_df = pd.read_sql(query_effectifs, conn)
        ventes_df = pd.read_sql(query_ventes, conn)

        effectifs_df['Anciennete'] = effectifs_df['Date_In'].apply(calculate_anciennete)
        effectifs_df['Birth_Date'] = pd.to_datetime(effectifs_df['Birth_Date'])
        effectifs_df['Date_In'] = pd.to_datetime(effectifs_df['Date_In'])
        effectifs_df['Age'] = effectifs_df['Birth_Date'].apply(calculate_age)

        return effectifs_df, ventes_df

    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la récupération des données : {err}")
        return None, None
    finally:
        if conn and conn.is_connected():
            conn.close()

def plot_charts(effectifs_df, ventes_df):
    competence_counts = effectifs_df['Competence'].value_counts().reset_index()
    competence_counts.columns = ['Competence', 'Nombre d\'Agents']

    fig1 = px.bar(
        competence_counts, 
        x='Competence', 
        y='Nombre d\'Agents', 
        title="Nombre d'agents par compétence",
        text_auto=True,  # Ajoute les valeurs sur les barres
        color='Nombre d\'Agents',
        color_continuous_scale=['#040233', '#bb8654', '#ffe7ad']
    )
    
    fig1.update_layout(
        xaxis_title="Compétence",
        yaxis_title="Nombre d'Agents",
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF'
    )

    ventes_df['Competence'] = ventes_df['ID_Citrix'].map(effectifs_df.set_index('ID_Citrix')['Competence'])
    vente_competence = ventes_df.groupby('Competence')['Montant'].count().reset_index()
    vente_competence.columns = ['Competence', 'Nombre de Ventes']

    fig2 = px.bar(
        vente_competence, 
        x='Competence', 
        y='Nombre de Ventes', 
        title="Nombre de ventes par compétence",
        text_auto=True,  # Ajoute les valeurs sur les barres
        color='Nombre de Ventes',
        color_continuous_scale=['#040233', '#b28765', '#ffe7ad']
    )

    fig2.update_layout(
        xaxis_title="Compétence",
        yaxis_title="Nombre de Ventes",
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF'
    )

    ventes_offre_competence = ventes_df.groupby(['Competence', 'Offre'])['Montant'].sum().reset_index()
    
    fig3 = px.bar(
        ventes_offre_competence, 
        x='Offre', 
        y='Montant', 
        text_auto=True,  # Ajoute les valeurs sur les barres
        color='Montant',
        color_continuous_scale=['#040233', '#bb8654', '#ffe7ad'],
        title="Ventes par offre et par compétence",
        facet_col='Competence'
    )

    fig3.update_layout(
        xaxis_title="Offre",
        yaxis_title="Montant des Ventes",
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF'
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1)
    with col2:
        st.plotly_chart(fig2)

    st.plotly_chart(fig3)  

def export_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Effectifs")
    output.seek(0)
    return output

def global_page():
    add_custom_css()
    col1, col2 = st.columns([1, 9])

    with col1:
        display_logo(os.path.join("Images", "AC.png"), width=120)

    with col2:
        st.header("Données des Effectifs", anchor=False)

    effectifs_df, ventes_df = get_effectifs_data()

    if effectifs_df is not None and ventes_df is not None:
        plot_charts(effectifs_df, ventes_df)
        add_custom_css()
        with st.expander("Voir l'Effectif global"):
            st.dataframe(
                
                effectifs_df.style.set_properties(**{
                    'background-color': '#FFFFFF',
                    'color': '#040233',
                    'border-color': '#b28765'
                })
            )

            st.download_button(
                
                label="Exporter en Excel",
                data=export_to_excel(effectifs_df),
                file_name="effectifs.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("Aucune donnée à afficher.")

if __name__ == "__main__":
    global_page()
