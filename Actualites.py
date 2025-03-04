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


def page_Actualites():
    """Page pour afficher les membres de l'équipe et leurs performances."""
    # Afficher le logo de l'entreprise
    col1, col2 = st.columns([2, 4])
    with col1:
        display_logo(os.path.join("Images", "AC.png"), width=180)
    with col2:
        st.header("Actualités", anchor=False)
    
    # Afficher l'image "Rappel_accor-live-limitless-status-levels.png"
    
    image_path = os.path.join("Images", "Rappel_accor1.png")
        
        # Vérifier si le fichier existe
    if not os.path.exists(image_path):
            st.error(f"Le fichier {image_path} n'existe pas.")
    else:
            try:
                image = Image.open(image_path)
                st.image(image, width=2200)  # Afficher l'image avec une largeur de 400 pixels
            except Exception as e:
                st.error(f"Erreur lors du chargement de l'image : {e}")

