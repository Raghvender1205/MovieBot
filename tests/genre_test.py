import requests

url = "https://api.themoviedb.org/3/genre/movie/list?language=en"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlMzI3YzlhYzkzYTc5MjE5ZWRkYWEwYTc3YTVhZmY0MSIsInN1YiI6IjY0YWJkZGI3YjY4NmI5MDBjYzBhN2NmYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.xoS2li5qtrVLV9ix5I_AiGb33yE4PckHpmiwuRhi0mI"
}

response = requests.get(url, headers=headers)

print(response.text)