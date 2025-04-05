import os
import discord
from discord.ext import tasks, commands
import requests
import random
import asyncio
from urllib.parse import urlencode
from datetime import datetime

# Configuration via variables d'environnement
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BASE_URL = 'https://api.spotify.com/v1/'

# Récupération des channels/genres depuis une variable d'environnement
# Format : "CHANNEL1_ID:GENRE1,CHANNEL2_ID:GENRE2"
CHANNEL_GENRES = {
    int(k): v for k, v in [
        item.split(':') for item in 
        os.getenv('CHANNEL_GENRES', '').split(',') 
        if item
    ]
} if os.getenv('CHANNEL_GENRES') else {
    1216808714514862290: "pop OR eighties",  # Remplacez par l'ID de votre channel
    1225851423812747294: "afrobeat",  # Remplacez par l'ID de votre channel
    1219779667867992114: "ballads OR slow",  # Remplacez par l'ID de votre channel
    1220840177514184805: "folk OR acoustic",  # Remplacez par l'ID de votre channel
    1221128942296240209: "dance OR electro OR edm",  # Remplacez par l'ID de votre channel
    1220846722952069240: "rock OR punk",  # Remplacez par l'ID de votre channel
    1220840281386123295: "soul OR jazz",  # Remplacez par l'ID de votre channel
    1220840221189472267: "house OR techno",  # Remplacez par l'ID de votre channel
    1220838836397936831: "hip-hop",  # Remplacez par l'ID de votre channel
    1217943769312399421: "français",  # Remplacez par l'ID de votre channel
}

POST_INTERVAL = int(os.getenv('POST_INTERVAL', 3600))  # 1 heure par défaut

class SpotifyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        # Remove command_sync_flags as it's not needed
        super().__init__(command_prefix='!', intents=intents)
        self.spotify_token = None
        self.token_expiry = None
        self.add_commands()

    async def setup_hook(self):
        # Ajout de l'enregistrement des commandes slash
        await self.tree.sync()
        self.post_tracks.start()

    def add_commands(self):
        # Nouvelle commande slash
        @self.tree.command(name="suggestion", description="Obtenir une suggestion musicale pour ce channel")
        async def suggestion(interaction: discord.Interaction):
            channel_id = interaction.channel_id
            if channel_id not in CHANNEL_GENRES:
                await interaction.response.send_message("Ce channel n'est pas configuré pour les suggestions musicales !", ephemeral=True)
                return

            await interaction.response.defer()
            
            try:
                genre = CHANNEL_GENRES[channel_id]
                track = await self.get_random_track(genre)
                await interaction.followup.send(f"Voici une suggestion pour vous : {track['url']}")
            except Exception as e:
                await interaction.followup.send("Désolé, une erreur est survenue lors de la recherche d'une piste.", ephemeral=True)
                print(f"Erreur suggestion : {str(e)}")

    def get_spotify_token(self):
        if self.spotify_token and datetime.now().timestamp() < self.token_expiry:
            return self.spotify_token
            
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
        }
        
        response = requests.post(auth_url, data=auth_data)
        response.raise_for_status()
        data = response.json()
        self.spotify_token = data['access_token']
        self.token_expiry = datetime.now().timestamp() + data['expires_in'] - 600
        return self.spotify_token

    async def get_random_track(self, genre=None, max_retries=3):
        token = self.get_spotify_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        for attempt in range(max_retries):
            try:
                query = genre or 'top'
                search_url = f"{BASE_URL}search?{urlencode({'q': query, 'type': 'playlist', 'limit': 50})}"
                response = requests.get(search_url, headers=headers)
                response.raise_for_status()
                
                playlist = random.choice(response.json().get('playlists', {}).get('items', []))
                tracks_url = f"{BASE_URL}playlists/{playlist['id']}/tracks"
                tracks_response = requests.get(tracks_url, headers=headers)
                tracks_response.raise_for_status()
                
                track = random.choice(tracks_response.json().get('items', []))['track']
                return {
                    'url': track['external_urls']['spotify'],
                    'name': track.get('name', 'Titre inconnu'),
                    'artist': ', '.join([a.get('name', '?') for a in track.get('artists', [])])
                }
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2)

    @tasks.loop(seconds=POST_INTERVAL)
    async def post_tracks(self):
        if not CHANNEL_GENRES:
            return
            
        channel_id, genre = random.choice(list(CHANNEL_GENRES.items()))
        channel = self.get_channel(channel_id)
        
        if channel:
            try:
                track = await self.get_random_track(genre)
                await channel.send(track['url'])
                print(f"Posté dans #{channel.name} : {track['url']}")
            except Exception as e:
                print(f"Erreur : {str(e)}")

    @post_tracks.before_loop
    async def before_post_tracks(self):
        await self.wait_until_ready()

# Validation des variables d'environnement
if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, DISCORD_TOKEN]):
    raise ValueError("Variables d'environnement manquantes !")

bot = SpotifyBot()
bot.run(DISCORD_TOKEN)