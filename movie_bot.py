import discord
import requests
import random
import json
import time
import os
from dotenv import load_dotenv

from tv_shows import fetch_tv_shows, fetch_tv_shows_by_genre

# Keys
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
    
    if message.content.startswith('!test'):
        channel = message.channel
        await channel.send('Bot is working!')
    
    if message.content.startswith('!help'):
        await show_help(message)

    if message.content.startswith('!recommend'):
        if message.content.startswith('!recommend list'):
            await recommend_movie_list(message)
        elif message.content.startswith('!recommend tv'):
            await recommend_tv_show_list(message)
        else:
            await recommend_movie(message)


async def recommend_movie(message):
    """
    Function to recommend a single movie either random or by genre
    Params 
        - message -> eg:- !recommend action
    Returns
        - A movie recommendation on the discord channel 
    """
    genre = message.content.split(' ')[1]
    if genre.lower() == 'random':
        movie_data = fetch_random_movie()
    else:
        genre_id = get_genre_id(genre)
        if genre_id is None:
            await message.channel.send("Sorry, I couldn't find the genre ID for the specified genre")
            return 
        movie_data = fetch_movie_by_genre_id(genre_id)

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


async def recommend_movie_list(message):
    """
    Function to recommend a list of movies by genre
    Params
        - message -> eg:- !recommend list action
    Returns
        - A recommend list of movies by that genre
    """
    genre = message.content.split(' ')[2]
    genre_id = get_genre_id(genre)
    if genre_id is None:
        await message.channel.send("Sorry, I couldn't find any recommendations for that genre")
        return
    movie_data = fetch_movies_by_genre(genre_id)

    if movie_data is None or not movie_data:
        await message.channel.send("Sorry, I couldn't find any recommendations for this genre")
        return

    try:
        embed = discord.Embed(title=f'Movie recommmendations for {genre}', description="")
        for i, movie in enumerate(movie_data, start=1):
            title = movie['title']
            overview = movie['overview']
            if len(overview) > 2000:
                overview = overview[:1997] + '...'
            embed.add_field(name=f"{i}. {title}", value=overview, inline=False)
            if i % 10 == 0:
                await message.channel.send(embed=embed)
                embed.clear_fields()
        
        if len(embed.fields) > 0:
            await message.channel.send(embed=embed)

    except KeyError:
        await message.channel.send('Sorry, there was an issue with the movie recommendation. Please try again later')


def fetch_random_movie():
    """
    Fetch a random movie recommendation using TMDB API
    """
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


def fetch_genre_list():
    """
    Fetch Genre list from the TMDB database.
    """
    api_key = os.getenv('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
    try:
        retries = 3
        for attempt in range(retries):
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data['genres']
            else:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                else:
                    print(f"Error while fetching genre list: {response.status_code}")
                    return None
    except requests.exceptions.RequestException as e:
        print('Error occurred while fetching genre list:', str(e))
        return None


def get_genre_id(genre):
    """
    Get genre id from the genre list function
    Params
        - genre
    Returns
        - genre_id
    """
    global GENRE_LIST
    
    if GENRE_LIST is None:
        GENRE_LIST = fetch_genre_list()
    if GENRE_LIST is not None:
        genre_l = genre.lower()
        print("Available Genres:", [g['name'] for g in GENRE_LIST])
        for g in GENRE_LIST:
            if g['name'].lower() == genre_l:
                return g['id']
    print("Genre ID not found for:", genre)  # Debugging statement
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


def fetch_movies_by_genre(genre_id):
    """
    Fetch movies by genre for recommend list of movies function
    Params
        - genre_id
    Returns
        - movies_data -> list of dict containing movie information
    """
    api_key = os.getenv('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre_id}'

    try:
        retries = 3
        for i in range(retries):
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
                if i < retries - 1:
                    time.sleep(1)
                    continue
                else:
                    print('Error while fetching movies by genre ID: ')
                    return None
    except requests.exceptions.RequestException as e:
        print('Error while fetching movies by genre ID: ', str(e))
        return None 


async def show_help(message):
    """
    Function to list all the commands for the bot 
    """
    help_messages = [
        "Available commands:",
        "- !test: Check if the bot is working",
        "- !recommend <genre>: Get a movie recommendation for that genre",
        "- !recommend random: Get a movie recommendation by random",
        "- !recommend list <genre>: Get a list of movie recommendations by genre",
        "- !help: Show this help message"
    ]
    help_message = "\n".join(help_messages)
    await message.channel.send(help_message)


async def recommend_tv_show_list(message):
    genre = message.content.split(' ')[2]
    genre_id = get_genre_id(genre)
    if genre_id is None:
        await message.channel.send("Sorry, I couldn't find any TV show recommendations for this genre")
        return
    tv_shows = fetch_tv_shows_by_genre(genre)
    if not tv_shows:
        await message.channel.send("Sorry, I couldn't find any TV show recommmendations for this genre")
        return
    
    try:
        embed = discord.Embed(title=f'TV show recommendations for {genre}', description='')
        for i, show in enumerate(tv_shows, start=1):
            name = show.get("name", "Unknown")
            overview = show.get("overview", "")
            if len(overview) > 2000:
                overview = overview[:1997] + "..."
            embed.add_field(name=f"{i}. {name}", value=overview, inline=False)
            if i % 10 == 0:
                await message.channel.send(embed=embed)
                embed.clear_fields()
        if len(embed.fields) > 0:
            await message.channel.send(embed=embed)
    except KeyError:
        await message.channel.send("Sorry, there was an issue with the TV show recommendation. Please try again later.")

if __name__ == '__main__':
    client.run(str(token))