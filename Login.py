import streamlit as st
from streamlit_option_menu import option_menu

from Plannings import Planning_page
from Agent import *
from Global import global_page
from Conges import Conge_page
from Evenements import *
from Retards import *
from datetime import datetime
from db_utils import get_db_connection, get_user_name, display_logo, color_cells,login_page

# Fonction pour afficher un logo
def display_logo(image_path, width):
    try:
        img = Image.open(image_path)
        st.image(img, width=width)
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image : {e}")

