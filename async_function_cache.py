import asyncio
import aiohttp
import time
from aiocache import cached
from aiocache.serializers import JsonSerializer

# Limite de concurrence (nombre maximum de requêtes simultanées)
MAX_CONCURRENT_REQUESTS = 5

# Durée d'expiration du cache (1 heure en secondes)
CACHE_EXPIRATION = 3600

# Génère les URLs des jeux
def generate_urls(base_url, start_id, end_id):
    urls = [f"{base_url}/api/game/{game_id}" for game_id in range(start_id, end_id + 1)]
    return urls

# Fonction pour effectuer une requête GET asynchrone avec cache
@cached(ttl=CACHE_EXPIRATION, serializer=JsonSerializer())
async def fetch(session, url):
    """
    Effectue une requête GET asynchrone avec un cache de 1 heure.
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                result = await response.json()  # Supposons que la réponse soit en JSON
                print(f"Success: {url} - {result.get('title', 'No title')}")
                return result
            else:
                print(f"Failed with status {response.status}: {url}")
                return None
    except Exception as e:
        print(f"Exception for {url}: {str(e)}")
        return None

# Gestionnaire de requêtes asynchrone avec un sémaphore pour limiter la concurrence
async def bound_fetch(sem, session, url):
    async with sem:
        return await fetch(session, url)

# Fonction principale qui envoie un grand nombre de requêtes
async def run(load, base_url, start_id, end_id):
    urls = generate_urls(base_url, start_id, end_id)  # Génère les URLs des jeux
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)  # Limite la concurrence

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(load):
            url = urls[i % len(urls)]  # Répartit les requêtes entre les différentes URLs
            task = asyncio.create_task(bound_fetch(sem, session, url))
            tasks.append(task)
        
        # Attendre que toutes les tâches soient terminées
        results = await asyncio.gather(*tasks)
        return results

# Script pour simuler la charge
def simulate_load(load, base_url, start_id, end_id):
    start_time = time.time()
    
    # Exécuter la boucle asyncio
    asyncio.run(run(load, base_url, start_id, end_id))
    
    end_time = time.time()
    print(f"Completed {load} requests in {end_time - start_time} seconds")

# Simulation d'une charge élevée avec des requêtes vers plusieurs routes
if __name__ == "__main__":
    total_requests = 100  # Nombre total de requêtes à effectuer
    base_url = "http://localhost:8080"  # Votre base URL de l'API Flask
    start_game_id = 480  # ID de départ des jeux
    end_game_id = 500  # ID de fin des jeux (ajustez selon vos besoins)
    
    simulate_load(total_requests, base_url, start_game_id, end_game_id)
