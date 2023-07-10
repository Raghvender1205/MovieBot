import discord
import requests
import random
import json
import time
import os
from dotenv import load_dotenv

# Keys
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name} ({client.user.id})') # type: ignore

@client.event
async def on_message(message):
    if message.author == client.user:
        return 
    if message.content.startswith('!test'):
        channel = message.channel
        await channel.send('Bot is working!')
    if message.content.startswith('!recommend'):
        await recommend_movie(message)

async def recommend_movie(message):
    genre = message.content.split(' ')[1]
    if genre.lower() == 'random':
        movie_data = fetch_random_movie()
    else:
        movie_data = fetch_movie_by_genre(genre)
        print(movie_data)
    if movie_data is None:
        await message.channel.send("Sorry, I couldn't find a recommendation at the moment")
        return
    
    try: 
        # Extract info
        title = movie_data['title']
        overview = movie_data['overview']
        poster_url = movie_data['poster_url']

        # Send recommendation
        rec = discord.Embed(title=title, description=overview)
        rec.set_image(url=poster_url)
        await message.channel.send(embed=rec)
    except KeyError:
        await message.channel.send('Sorry, There was an issue with movie recommendation. Please Try again later.')

def fetch_random_movie():
    api_key = os.getenv('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'
    
    try:
        retries = 3
        for i in range(retries):
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                results = data['results']
                random_movie = random.choice(results)
                movie_data = {
                    'title': random_movie['title'],
                    'overview': random_movie['overview'],
                    'poster_url': f"https://image.tmdb.org/t/p/original/{random_movie['poster_path']}"
                }
            
                return movie_data
            else:
                if i < retries - 1:
                    time.sleep(1)
                    continue
                else:
                    print('Error while fetching random movie: ')
                    return None
    except requests.exceptions.RequestException as e:
        print('Error while fetching random movie: ', str(e))
        return None

def get_genre_id(genre):
    api_key = os.getenv('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            genres = data['genres']
            print(genres)
            for i in genres:
                if i['name'].lower == genre.lower():
                    return i['id']
    except requests.exceptions.RequestException as e:
        print('Error while fetching genre list: ', str(e))
        return None

def fetch_movie_by_genre(genre):
    api_key = os.getenv('TMDB_API_KEY')
    genre_id = get_genre_id(genre)

    if genre_id is None:
        return None
    # print('genre id')
    # url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_id}'
    url = f'https://api.themoviedb.org/3/discover/movie?&include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&with_genres={genre_id}'
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlMzI3YzlhYzkzYTc5MjE5ZWRkYWEwYTc3YTVhZmY0MSIsInN1YiI6IjY0YWJkZGI3YjY4NmI5MDBjYzBhN2NmYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.xoS2li5qtrVLV9ix5I_AiGb33yE4PckHpmiwuRhi0mI"
    }
    try:
        response = requests.get(url, headers=headers)
        # print(response)
        if response.status_code == 200:
            data = response.json()
            results = data['results']
            if results:
                random_movie = random.choice(results)
                movie_data = {
                    'title': random_movie['title'],
                    'overview': random_movie['overview'],
                    'poster_url': f"https://image.tmdb.org/t/p/original/{random_movie['poster_path']}"
                }
                return movie_data
            else:
                return None
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching {genre} movie:", str(e))
        return None
    
if __name__ == '__main__':
    client.run(str(token))