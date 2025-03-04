import streamlit as st
from streamlit_option_menu import option_menu
import os
from db_utils import get_user_name, display_logo, authenticate, get_user_status, login_page
from Plannings import Planning_page
from Global import global_page
from Conges import Conge_page
from Evenements import Evenement_page
from Retards import retards_Page
from Equipes import page_equipes
from Actualites import page_Actualites

# Style CSS personnalisé
def add_custom_css():
    custom_css = """
    <style>
         footer {visibility: hidden;}
    
    /* Styles pour les boutons */
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
    
    /* Styles pour les sélecteurs */
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
    
    /* Styles pour la barre latérale */
    .css-1d391kg {
        background-color: #040233; /* Couleur de fond de la barre latérale */
        color: white; /* Couleur du texte dans la barre latérale */
    }
    
    /* Styles pour les titres dans la barre latérale */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: white;
    }
    
    /* Styles pour les boutons dans la barre latérale */
    .css-1d391kg .stButton>button {
        background-color: #bb8654;
        color: white;
    }
    .css-1d391kg .stButton>button:hover {
        background-color: #ffe7ad;
        color: #bb8654;
    }
    
    /* Styles pour les sélecteurs dans la barre latérale */
    .css-1d391kg .stSelectbox>div>div>input {
        background-color: #ffe7ad;
        color: #bb8654;
    }
    .css-1d391kg .stSelectbox>div>div>input:focus {
        background-color: #bb8654;
        color: white;
    }
    .css-1d391kg .stSelectbox label {
        color: #b28765;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# Appliquer le style CSS personnalisé
add_custom_css()

# Fonction principale pour démarrer l'application Streamlit
def main():
    # Initialisation des variables de session si nécessaire
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "Statut" not in st.session_state:
        st.session_state["Statut"] = None
    if "ID_Citrix" not in st.session_state:
        st.session_state["ID_Citrix"] = None
    if "Nom_Prenom" not in st.session_state:
        st.session_state["Nom_Prenom"] = "Utilisateur"
    if "ID_Citrix_User" not in st.session_state:  # Assure-toi que cette clé est bien initialisée
        st.session_state["ID_Citrix_User"] = None

    # Page de connexion si l'utilisateur n'est pas authentifié
    if not st.session_state["authenticated"]:
        col1, col2 = st.columns([1, 2])

        with col1:
            display_logo(os.path.join("Images", "AC.png"), width=200)

        with col2:
            #st.subheader("Page de connexion")
            login = st.text_input("Nom d'utilisateur : ")
            password = st.text_input("Mot de passe :", type="password")

            col1, col2 ,col3 = st.columns([1, 1, 1])
            with col1:
                st.header("")
            with col2:
                if st.button("Se connecter", use_container_width=True):
                    # Authentifier l'utilisateur
                    is_authenticated, ID_Citrix_User = authenticate(login, password)
                    if is_authenticated:
                        statut = get_user_status(ID_Citrix_User)
                        # Mise à jour de la session avec les informations nécessaires
                        st.session_state["authenticated"] = True
                        st.session_state["Statut"] = statut
                        st.session_state["ID_Citrix"] = ID_Citrix_User
                        st.session_state["Nom_Prenom"] = get_user_name(ID_Citrix_User)
                        st.session_state["ID_Citrix_User"] = ID_Citrix_User  # Initialisation de la clé ID_Citrix_User
                        st.success(f"Connexion réussie en tant que {statut} !")
                        st.rerun()  # Recharger la page après authentification
                    else:
                        st.error("Échec de l'authentification. Veuillez vérifier vos informations d'identification.")
            with col3:
                if st.button("**Annuler**", use_container_width=True):
                    st.info("Aucune modification n'a été effectuée.")

    else:
        # Si l'utilisateur est authentifié, on récupère l'ID_Citrix_User dans la session
        ID_Citrix_User = st.session_state["ID_Citrix_User"]
        statut = st.session_state["Statut"]
        NomP = st.session_state['Nom_Prenom']

        # Mise à jour de la sidebar selon le rôle
        if statut == "Agent":
            with st.sidebar:
                selected = option_menu(
                    f"Menu {NomP}",
                    ["Actualités", "Planning", "Congés"],
                    icons=["calendar", "list-task"],
                    menu_icon="menu",
                    default_index=0,
                    orientation="vertical",
                    styles={
                        "container": {"background-color": "#040233"},
                        "icon": {"color": "#ffe39c"},
                        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "white"},
                        "nav-link-selected": {"background-color": "#ebb26d"},
                    },
                )

            if selected == "Actualités":
                page_Actualites()
            elif selected == "Planning":
                Planning_page()
            elif selected == "Congés":
                Conge_page()

        elif statut in ["Manager"]:
            with st.sidebar:
                selected = option_menu(
                    f"Menu {NomP}",
                    ["Global", "Retards", "Equipe"],
                    icons=["house", "clock", "calendar-event"],
                    menu_icon="menu",
                    default_index=0,
                    orientation="vertical",
                    styles={
                        "container": {"background-color": "#040233"},
                        "icon": {"color": "#ffe39c"},
                        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "white"},
                        "nav-link-selected": {"background-color": "#ebb26d"},
                    },
                )
            if selected == "Global":
                global_page()
            elif selected == "Retards":
                retards_Page()
            elif selected == "Equipe":
                page_equipes()

        elif statut in ["Commando"]:
            with st.sidebar:
                selected = option_menu(
                    f"Menu {NomP}",
                    ["Global", "Retards", "Equipe", "Evenements"],
                    icons=["house", "clock", "calendar-event", "gear"],
                    menu_icon="menu",
                    default_index=0,
                    orientation="vertical",
                    styles={
                        "container": {"background-color": "#040233"},
                        "icon": {"color": "#ffe39c"},
                        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "white"},
                        "nav-link-selected": {"background-color": "#ebb26d"},
                    },
                )

                if selected == "Global":
                    global_page()
                elif selected == "Retards":
                    retards_Page()
                elif selected == "Evenements":
                    Evenement_page()
                elif selected == "Equipe":
                    page_equipes()

        elif statut == "Support":
            with st.sidebar:
                st.markdown(f"<h2 style='color: White;'>Bienvenue, <strong>{NomP}</strong>!</h2>", unsafe_allow_html=True)
                selected = option_menu(
                    f"Menu {NomP}",
                    ["Global", "Cotec"],
                    icons=["house", "gear"],
                    menu_icon="menu",
                    default_index=0,
                    orientation="vertical",
                    styles={
                        "container": {"background-color": "#040233"},
                        "icon": {"color": "#ffe39c"},
                        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "white"},
                        "nav-link-selected": {"background-color": "#ebb26d"},
                    },
                )
            if selected == "Global":
                global_page()
            elif selected == "Retards":
                retards_Page()
            elif selected == "Evenements":
                Evenement_page()
            elif selected == "Equipe":
                st.header("Page Equipe")

if __name__ == "__main__":
    main()