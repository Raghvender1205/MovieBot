# MovieBot: Movie Recommendation 
A Movie Recommendation bot for discord.

Invite Link for Discord

```
https://discord.com/api/oauth2/authorize?client_id=1127887065246347366&permissions=1099511627776&scope=bot
```

It uses 
1. `TMDB` (The Movie Database) for the database of movies and its API
2. `discord` for its integration for the bot

## Usage
1. It currently performs two actions
- `!recommend random`:- This recommends us a random movie
- `!recommend <genre>`:- This feature recommends the movie based on the `<genre>` query.
- `!recommend list <genre>`:- This feature recommends a list of movies based on the `<genre>` query.
- `!recommend tv <genre>`:- This feature recommends a list  of tv shows based on the `<genre>`.


## TODO
1.  Fix the API timeout issue
2.  Try to add UI, Buttons for interactivity
3.  Add more features to support the full `TMDB` API.