import streamlit as st
import pandas as pd
import requests
import folium
from geopy.distance import geodesic

# Fonction pour appeler l'API OpenRouteService
def call_openrouteservice(coordinates, profile):
    url = f'https://api.openrouteservice.org/v2/directions/{profile}/geojson'
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': '5b3ce3597851110001cf6248a77c9061ac354f63b239407848bb9f8f',
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {
        "coordinates": coordinates

    }
    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        try:
            error_message = response.json()['error']['message']
        except Exception as e:
            error_message = f"Erreur non spécifiée : {str(e)}"
            
        st.error(f"Erreur lors de l'appel à l'API OpenRouteService : {response.status_code}, {error_message}")
        return None



def load_data():
    df = pd.read_csv('clusters_data.csv')
    return df

# Fonction pour calculer la distance entre deux points (en kilomètres)
def calculate_distance(point1, point2):
    return geodesic(point1, point2).kilometers

# Fonction principale de l'application Streamlit
def main():
    st.title('OpenRouteService Directions & Carte avec Itinéraire')

    # Charger les données depuis le CSV
    df = load_data()

    with open("clusters_map.html", "r", encoding="utf-8") as file:
                    html_code = file.read()
                    st.components.v1.html(html_code, width=800, height=600)
    # Sélection de la couleur par l'utilisateur
    selected_color = st.selectbox('Choisir une couleur :', df['color'].unique())

    # Filtrer les données en fonction de la couleur sélectionnée
    filtered_data = df[df['color'] == selected_color]

    # Afficher les données filtrées
    st.write(f"Coordonnées pour la couleur '{selected_color}':")
    st.dataframe(filtered_data[['label_fr', 'latitude', 'longitude']])

    # Préparer les coordonnées pour l'appel API (assurez-vous de l'ordre correct : [longitude, latitude])
    coordinates = filtered_data[['longitude', 'latitude']].values.tolist()

    # Sélection du mode de transport
    transport_modes = ['driving-car', 'cycling-regular', 'foot-walking', 'driving-hgv']
    selected_transport_mode = st.selectbox('Choisir le mode de transport :', transport_modes)

    # Afficher la carte avec les marqueurs des coordonnées
    st.subheader('Carte des emplacements')
    map_center = [filtered_data['latitude'].mean(), filtered_data['longitude'].mean()]
    m = folium.Map(location=map_center, tiles='cartodbpositron', zoom_start=13)

    # Ajouter des marqueurs pour chaque point
    for index, row in filtered_data.iterrows():
        popup_text = f"{row['label_fr']} (ligne {index + 1})"
        folium.Marker([row['latitude'], row['longitude']], popup=popup_text).add_to(m)

    # Tracer l'itinéraire avec OpenRouteService
    if st.button('Afficher l\'itinéraire'):
        st.write('Envoi de la requête à OpenRouteService...')
        response = call_openrouteservice(coordinates, selected_transport_mode)

        if response:
            # Vérifier si des routes ont été trouvées dans la réponse
            if 'features' in response and len(response['features']) > 0:
                # Récupérer les coordonnées de l'itinéraire
                route_coordinates = []
                for coord in response['features'][0]['geometry']['coordinates']:
                    route_coordinates.append(list(reversed(coord)))
                
                # Ajouter la ligne de l'itinéraire à la carte
                folium.PolyLine(locations=route_coordinates, color='blue', weight=5).add_to(m)

                # Calculer et afficher les distances entre chaque paire de destinations
                st.subheader('Distances entre les destinations (en kilomètres)')
                distances = []
                for i in range(len(coordinates) - 1):
                    coord1 = tuple(coordinates[i])
                    coord2 = tuple(coordinates[i + 1])
                    distance = calculate_distance(coord1, coord2)
                    distances.append({
                        'De': filtered_data.iloc[i]['label_fr'],
                        'À': filtered_data.iloc[i + 1]['label_fr'],
                        'Distance (km)': distance
                    })
                
                st.dataframe(pd.DataFrame(distances))

                # Convertir la carte Folium en HTML
                m.save('map.html')
                
                # Afficher la carte dans Streamlit à l'aide de l'iframe
                with open('map.html', 'r', encoding='utf-8') as f:
                    html = f.read()
                st.components.v1.html(html, height=600)

            else:
                st.error('Aucune route trouvée pour les coordonnées fournies.')
        else:
            st.error('Erreur lors de la récupération des données de l\'API OpenRouteService.')

if __name__ == '__main__':
    main()
