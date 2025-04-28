# Spotify-Discord-Bot

A Dockerized Discord bot that posts random Spotify tracks to specified channels at regular intervals, filtered by music genres.

## Features 🎵

- Automatically posts random tracks to configured channels based on specified genres
- `/suggestion` command to get an instant music suggestion in any configured channel
- Customizable posting intervals
- Genre-specific channel configuration

## Configuration ⚙️

Create a `.env` file in the root directory with the following structure:

```env
# Spotify Configuration (required)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
DISCORD_TOKEN=your_discord_bot_token

# Channel and genre configuration
# Format: CHANNEL_ID:GENRE,CHANNEL_ID:GENRE,...
CHANNEL_GENRES=123456789:pop OR eighties,987654321:rock OR punk

# Post interval in seconds (default: 3600)
POST_INTERVAL=3600
```

## Deployment 🚀

```bash
# Build the image
docker build -t spotify-bot .

# Run the container
docker run -d --restart always --env-file .env --name spotify-bot spotify-bot
```

## Authorizations in Discord Developer portal 🔐

Choose your app, then go to `OAuth2`, then go to the section OAuth2 URL Generator
- In scopes, check `bot`
- Then, below and under Texts Permission, check `Send Messages`.

You can then generate the invite link for your bot.
