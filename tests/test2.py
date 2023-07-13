import discord
import requests
import random
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

GENRE_LIST = None

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name} ({client.user.id})') # type: ignore

@client.event
async def on_message(message):
    if message.author == client.user:
        return 

    if message.content.startswith('!recommend'):
        command = message.content.split(' ')
        if len(command) < 2:
            await message.channel.send("Invalid command format. Please use the correct format: '!recommend random' or '!recommend <genre>' or '!recommend list <genre>'")
        
        cmd = command[2]
        if cmd == 'random':
            await recommend_random_movie(message)
        elif cmd == 'list':
            genre = ''.join(command[2:])
            await recommend_movie_list(message, genre)
        else:
            genre = ' '.join(command[1:])
            await recommend_movie(message, genre)

async def recommend_random_movie(message):
    movie_data = fetch_random_movie()
    if movie_data is None:
        await message.channel.send("Sorry, I couldn't find a recommendation at the moment")
        return

    try: 
        title = movie_data['title']
        overview = movie_data['overview']
        poster_url = movie_data['poster_url']

        rec = discord.Embed(title=title, description=overview)
        rec.set_image(url=poster_url)

        await message.channel.send(embed=rec)
    except KeyError:
        await message.channel.send('Sorry, there was an issue with movie recommendation. Please try again later.')

async def recommend_movie_list(message, genre):
    genre_id = get_genre_id(genre)
    if genre_id is None:
        await message.channel.send("Sorry, I couldn't find the genre ID for the specified genre")
        return

    movie_data = fetch_movies_by_genre(genre_id)
    if movie_data is None or not movie_data:
        await message.channel.send("Sorry, I couldn't find any recommendations for this genre")
        return

    try:
        embed = discord.Embed(title=f'Movie Recommendations for {genre}', description="")
        for movie in movie_data:
            title = movie['title']
            overview = movie['overview']
            if len(overview) > 2000:
                overview = overview[:2000] + '...'
            embed.add_field(name=title, value=overview, inline=False)

        await message.channel.send(embed=embed)
    except KeyError:
        await message.channel.send('Sorry, there was an issue with the movie recommendation. Please try again later')

def fetch_random_movie():
    api_key = os.getenv('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'

    try:
        response = requests.get(url)
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
            print(f'Error while fetching random movie: {response.status_code}')
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching random movie: {str(e)}")
        return None

def fetch_genre_list():
    api_key = os.getenv('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            genres = data['genres']
            print(genres)
            return genres
        else:
            print(f"Error while fetching genre list: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching genre list: {str(e)}")
        return None

def get_genre_id(genre):
    global GENRE_LIST

    if GENRE_LIST is None:
        GENRE_LIST = fetch_genre_list()
    if GENRE_LIST is not None:
        genre_l = genre.lower()
        for g in GENRE_LIST:
            if g['name'].lower() == genre_l:
                return g['id']
    return None

def fetch_movies_by_genre(genre_id):
    api_key = os.getenv('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_id}'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = data['results']
            if results:
                movies_data = []
                for result in results:
                    movie_data = {
                        'title': result['title'],
                        'overview': result['overview'],
                        'poster_url': f"https://image.tmdb.org/t/p/original/{result['poster_path']}"
                    }
                    movies_data.append(movie_data)
                return movies_data
            else:
                return []
        else:
            print(f'Error while fetching movies by genre ID: {response.status_code}')
            return None
    except requests.exceptions.RequestException as e:
        print(f'Error while fetching movies by genre ID: {str(e)}')
        return None


def fetch_movie_by_genre_id(genre_id):
    """
    Fetch Movie by their genre_id
    Args
        - genre_id
    Returns
        movie_data -> A dict containing title, overview and poster_url for the movie
    """
    api_key = os.getenv('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_id}'
    try:
        response = requests.get(url)
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
            print(f'Error while fetching movie by genre ID: {response.status_code}')
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching movie by genre ID:", str(e))
        return None


async def recommend_movie(message, genre):
    genre_id = get_genre_id(genre)
    if genre_id is None:
        await message.channel.send("Sorry, I couldn't find the genre ID for the specified genre")
        return

    # Fetch a movie by genre
    movie_data = fetch_movie_by_genre_id(genre_id)
    if movie_data is None:
        await message.channel.send("Sorry, I couldn't find a recommendation at the moment")
        return

    # Extract movie details
    title = movie_data['title']
    overview = movie_data['overview']
    poster_url = movie_data['poster_url']

    # Create and send an embedded message with buttons
    embed = discord.Embed(title=title, description=overview)
    embed.set_image(url=poster_url)

if __name__ == '__main__':
    client.run(str(token))
