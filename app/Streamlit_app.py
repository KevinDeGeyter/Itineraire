import streamlit as st
from tab_parametres import main as parametres_tab
from tab_api import main as api_tab

def main():
    st.title("Projet Itineraire Data Engineer")

    menu = ["Paramètres de la requête", "Interrogation API"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Paramètres de la requête":
        parametres_tab()
    elif choice == "Interrogation API":
        api_tab()

if __name__ == "__main__":
    main()