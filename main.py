import os
from flask import Flask, jsonify, request
import requests
import urllib.parse
import time
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vérifier la clé
MOBY_API_KEY_V1 = 'moby_OSeFTYr0UvIjJZghgtUvMxOamwu'
MOBY_API_KEY = urllib.parse.quote(MOBY_API_KEY_V1)

if not MOBY_API_KEY:
    raise ValueError("La clé API MobyGames n'est pas valide.")



#Question1########################################################################################################################

def get_game_details(game_id):
    # URL pour obtenir les détails du jeu
    url = f"https://api.mobygames.com/v1/games/{game_id}"
    params = {
        'api_key': MOBY_API_KEY,
        'format': 'normal'  # Format complet
    }
    
    # Faire la requête GET
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        game_data = response.json()

        # Extraire les informations d'intérêt
        title = game_data.get('title', 'Titre non disponible')
        description = game_data.get('description', 'Description non disponible')
        
        # Extraire les genres
        genres = game_data.get('genres', [])
        genre_names = [genre['genre_name'] for genre in genres] if genres else ['Genres non disponibles']
        
        # Extraire les plateformes
        platforms = game_data.get('platforms', [])
        platform_names = [platform['platform_name'] for platform in platforms] if platforms else ['Plateformes non disponibles']
        
        # Extraire les captures d'écran
        screenshots = game_data.get('sample_screenshots', [])
        screenshot_urls = [screenshot['image'] for screenshot in screenshots] if screenshots else ['Aucune capture d\'écran disponible']
        
        # Retourner les informations sous forme de dictionnaire
        return {
            'title': title,
            'description': description,
            'genres': genre_names,
            'platforms': platform_names,
            'screenshots': screenshot_urls
        }
    else:
        return {'error': f"Impossible de récupérer les détails du jeu avec l'ID {game_id}. Statut: {response.status_code}"}
        # handle_error(response)





#Question2########################################################################################################################

def get_game_details_v2(game_id, max_retries=3, backoff_factor=2):
    """
    Récupère les détails d'un jeu spécifique à partir de l'API MobyGames.

    Args:
        game_id (int): L'ID du jeu à récupérer.
        max_retries (int): Nombre maximum de tentatives en cas d'échec.
        backoff_factor (int): Facteur de multiplication pour le délai d'attente entre les tentatives.

    Returns:
        dict: Détails du jeu ou informations d'erreur.
    """
    url = f"https://api.mobygames.com/v1/games/{game_id}"
    params = {
        'api_key': MOBY_API_KEY,
        'format': 'normal'  # Format complet
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

                # Extraire les genres
                genres = game_data.get('genres', [])
                genre_names = [genre['genre_name'] for genre in genres] if genres else ['Genres non disponibles']

                # Extraire les plateformes
                platforms = game_data.get('platforms', [])
                platform_names = [platform['platform_name'] for platform in platforms] if platforms else ['Plateformes non disponibles']

                # Extraire les captures d'écran
                screenshots = game_data.get('sample_screenshots', [])
                screenshot_urls = [screenshot['image'] for screenshot in screenshots] if screenshots else ['Aucune capture d\'écran disponible']

                # Retourner les informations sous forme de dictionnaire
                return {
                    'title': title,
                    'description': description,
                    'genres': genre_names,
                    'platforms': platform_names,
                    'screenshots': screenshot_urls
                }

            elif status_code == 400:
                logger.error(f"400 Bad Request: La requête est mal formée pour l'ID {game_id}.")
                return {'error': 'Bad Request: La requête est mal formée.'}

            elif status_code == 401:
                logger.error("401 Unauthorized: Clé API invalide ou absente.")
                return {'error': 'Unauthorized: Clé API invalide ou absente.'}

            elif status_code == 403:
                logger.error("403 Forbidden: Accès refusé.")
                return {'error': 'Forbidden: Accès refusé.'}

            elif status_code == 404:
                logger.error(f"404 Not Found: Jeu avec l'ID {game_id} non trouvé.")
                return {'error': f'Not Found: Jeu avec l\'ID {game_id} non trouvé.'}

            elif status_code == 429:
                # Trop de requêtes, attendre avant de réessayer
                logger.warning(f"429 Too Many Requests: Attente de {wait_time} secondes avant de réessayer...")
                time.sleep(wait_time)
                attempt += 1
                wait_time *= backoff_factor
                continue

            elif status_code in [500, 503]:
                # Erreurs de serveur, attendre avant de réessayer
                logger.warning(f"{status_code} Server Error: Attente de {wait_time} secondes avant de réessayer...")
                time.sleep(wait_time)
                attempt += 1
                wait_time *= backoff_factor
                continue

            else:
                # Autres erreurs
                logger.error(f"Erreur {status_code}: {response.text}")
                return {'error': f'Erreur {status_code}: {response.text}'}

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout: Attente de {wait_time} secondes avant de réessayer...")
            time.sleep(wait_time)
            attempt += 1
            wait_time *= backoff_factor
            continue

        except requests.exceptions.RequestException as e:
            logger.error(f"RequestException: {e}")
            return {'error': f'RequestException: {e}'}

    # Si toutes les tentatives échouent
    logger.error(f"Échec de la requête après {max_retries} tentatives.")
    return {'error': f"Échec de la requête après {max_retries} tentatives."}


if __name__ == '__main__':
    game_id = 550
    game_details = get_game_details_v2(game_id)
    print(game_details)