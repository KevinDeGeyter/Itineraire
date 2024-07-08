import streamlit as st
import subprocess
import pandas as pd
import requests

# Définition des paramètres par défaut
default_address = "Paris, France"
default_poi_types = ["Monument"]
default_radius = 50

# Fonction pour récupérer la latitude et la longitude à partir de l'adresse
def geocode(address):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': address,
        'format': 'json'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            return {
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon'])
            }
        else:
            return None
    else:
        st.error(f"Erreur lors de la récupération des coordonnées pour '{address}'")
        return None

# Fonction pour exécuter la requête et récupérer les résultats
def execute_query(latitude, longitude, poi_types, radius):
    poi_types_str = " ".join(poi_types)
    command = f"python3 Creation_Clusters.py --latitude {latitude} --longitude {longitude} --poi_types {poi_types_str} --radius {radius}"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        return True
    else:
        return False, stderr.decode('utf-8')

# Fonction pour charger les données du fichier CSV
@st.cache_data
def load_data():
    return pd.read_csv('clusters_data.csv')

# Fonction principale pour l'onglet de paramètres de requête
def main():
    st.title("Paramètres de la requête")

    # Entrée de l'adresse
    address = st.text_input("Entrez une adresse :", default_address)

    # Récupérer les coordonnées à partir de l'adresse
    coordinates = geocode(address)
    if coordinates:
        latitude = coordinates['latitude']
        longitude = coordinates['longitude']
    else:
        latitude = None
        longitude = None

    radius = st.text_input("Choisissez une distance maximale :", default_radius)
    # Sélection des types de points d'intérêt (POI)
    extended_poi_types = [
        "Culture", "Religion", "Sport", "Loisir", "Divertissement", "Hebergement", 
        "Restauration", "Boisson", "Banque", "Hebergement", "Autre", "Plage", 
        "Mobilité réduite", "Moyen de locomotion", "Montagne", "Antiquité", 
        "Histoire", "Musée", "Détente", "Bar", "Commerce local", "Point de vue", 
        "Nature", "Camping", "Cours d'eau", "Service", "Monument", "Jeunesse", 
        "Apprentissage", "Marché", "Vélo", "Magasin", "Animaux", "Location", 
        "Parcours", "Santé", "Information", "Militaire", "Parking", 
        "Marche à pied", "POI", "Piscine"
    ]

    poi_types = st.multiselect("Types de points d'intérêt :", extended_poi_types, default=default_poi_types)

    # Bouton pour exécuter la requête
    if st.button("Exécuter la requête"):
        if latitude is not None and longitude is not None:
            result = execute_query(latitude, longitude, poi_types, radius)
            if result == True:
                st.success("La requête a été exécutée avec succès !")
                # Affichage du résultat de la carte et du tableau CSV si disponible
                st.markdown("## Résultat de la carte")
                with open("clusters_map.html", "r", encoding="utf-8") as file:
                    html_code = file.read()
                    st.components.v1.html(html_code, width=800, height=600)
                
                st.markdown("## Données des établissements")
                try:
                    df = pd.read_csv("clusters_data.csv")
                    st.dataframe(df)
                except FileNotFoundError:
                    st.error("Le fichier csv est introuvable.")
            else:
                st.error(f"Erreur lors de l'exécution de la requête : {result}")
        else:
            st.warning("Adresse non valide. Veuillez entrer une adresse correcte.")
    
    st.markdown('[Accéder à l\'application Dash](http://localhost:8050/)')

if __name__ == "__main__":
    main()
