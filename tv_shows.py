import requests
import os 
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('TMDB_API_KEY')

def fetch_tv_shows(api_key):
    url = f'https://api.themoviedb.org/3/discover/tv?api_key={api_key}&sort_by=popularity.desc'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        return results
    else:
        print(f'Error fetching popular TV shows: ', response.status_code)
        return []
    

def fetch_tv_shows_by_genre(genre):
    url = f'https://api.themoviedb.org/3/discover/tv?api_key={api_key}&with_genres={genre}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        return results
    else:
        print('Error fetching TV shows by genre ID: ', response.status_code)
        return []