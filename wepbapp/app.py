import streamlit as st
import requests
import time

# Fonction get_game_details_v2 pour récupérer les détails du jeu via l'API
def get_game_details_v2(game_id, max_retries=3, backoff_factor=2):
    url = f"https://api.mobygames.com/v1/games/{game_id}"
    params = {
        'api_key': 'moby_OSeFTYr0UvIjJZghgtUvMxOamwu',  # Remplacez par votre clé API
        'format': 'normal'
    }

    attempt = 0
    wait_time = 1  # Temps initial d'attente en secondes

    while attempt < max_retries:
        try:
            response = requests.get(url, params=params, timeout=10)  # Timeout de 10 secondes
            status_code = response.status_code

            if status_code == 200:
                game_data = response.json()

                # Extraire les informations d'intérêt
                title = game_data.get('title', 'Titre non disponible')
                description = game_data.get('description', 'Description non disponible')
                genres = [genre['genre_name'] for genre in game_data.get('genres', [])]
                platforms = [platform['platform_name'] for platform in game_data.get('platforms', [])]
                screenshots = [screenshot['image'] for screenshot in game_data.get('sample_screenshots', [])]

                # Créer un dictionnaire structuré
                return {
                    'title': title,
                    'description': description,
                    'genres': genres,
                    'platforms': platforms,
                    'screenshots': screenshots
                }

            elif status_code == 400:
                st.error(f"400 Bad Request: La requête est mal formée pour l'ID {game_id}.")
                return {'error': 'Bad Request: La requête est mal formée.'}

            elif status_code == 401:
                st.error("401 Unauthorized: Clé API invalide ou absente.")
                return {'error': 'Unauthorized: Clé API invalide ou absente.'}

            elif status_code == 403:
                st.error("403 Forbidden: Accès refusé.")
                return {'error': 'Forbidden: Accès refusé.'}

            elif status_code == 404:
                st.error(f"404 Not Found: Jeu avec l'ID {game_id} non trouvé.")
                return {'error': f'Not Found: Jeu avec l\'ID {game_id} non trouvé.'}

            elif status_code == 429:
                # Trop de requêtes, attendre avant de réessayer
                st.warning(f"429 Too Many Requests: Attente de {wait_time} secondes avant de réessayer...")
                time.sleep(wait_time)
                attempt += 1
                wait_time *= backoff_factor
                continue

            elif status_code in [500, 503]:
                # Erreurs de serveur, attendre avant de réessayer
                st.warning(f"{status_code} Server Error: Attente de {wait_time} secondes avant de réessayer...")
                time.sleep(wait_time)
                attempt += 1
                wait_time *= backoff_factor
                continue

            else:
                st.error(f"Erreur {status_code}: {response.text}")
                return {'error': f'Erreur {status_code}: {response.text}'}

        except requests.exceptions.Timeout:
            st.warning(f"Timeout: Attente de {wait_time} secondes avant de réessayer...")
            time.sleep(wait_time)
            attempt += 1
            wait_time *= backoff_factor
            continue

        except requests.exceptions.RequestException as e:
            st.error(f"RequestException: {e}")
            return {'error': f'RequestException: {e}'}

    # Si toutes les tentatives échouent
    st.error(f"Échec de la requête après {max_retries} tentatives.")
    return {'error': f"Échec de la requête après {max_retries} tentatives."}

# Interface Streamlit
def main():
    st.title("Jeux - Récupération des Détails via API")
    
    # Demande de l'ID du jeu à l'utilisateur
    game_id = st.text_input("Entrez l'ID du jeu:", "550")
    
    if st.button("Récupérer les détails du jeu"):
        if game_id.isdigit():
            # Appel de la fonction pour récupérer les détails du jeu
            details = get_game_details_v2(int(game_id))
            
            if 'error' not in details:
                # Afficher les détails du jeu
                st.subheader(f"Titre: {details['title']}")
                st.write(f"Description: {details['description']}")
                
                st.subheader("Genres:")
                st.write(", ".join(details['genres']))
                
                st.subheader("Plateformes:")
                st.write(", ".join(details['platforms']))
                
                st.subheader("Captures d'écran:")
                for screenshot_url in details['screenshots']:
                    st.image(screenshot_url)
            else:
                st.error(details['error'])
        else:
            st.error("L'ID du jeu doit être un nombre.")

if __name__ == "__main__":
    main()
