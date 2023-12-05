import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os
import time
import logging
import requests
import base64
import aiohttp

SPOTIFY_CLIENT_ID = '9038179d98db4399bfb16ce70e25c2bd'
SPOTIFY_CLIENT_SECRET = '07596b8be1734221b40d5d758b37f082'
# Set up logging
logging.basicConfig(level=logging.INFO)

class MusicControls(discord.ui.View):
    def __init__(self, bot, interaction: discord.Interaction):
        super().__init__()
        self.bot = bot
        self.interaction = interaction
        logging.info("Music controls initialized.")
        
    @discord.ui.button(label="Pause", style=discord.ButtonStyle.grey)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.green)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.red)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()

    @discord.ui.button(label="Clear Queue", style=discord.ButtonStyle.grey, emoji="🗑️")
    async def clear_queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Clear the song queue for this guild
        guild_id = interaction.guild_id
        if guild_id in self.bot.get_cog("MusicCommands").song_queues:
            self.bot.get_cog("MusicCommands").song_queues[guild_id] = asyncio.Queue()
            await interaction.response.send_message("Song queue cleared.", ephemeral=True)
        else:
            await interaction.response.send_message("No queue to clear.", ephemeral=True)


class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queues = {}
        self.command_channels = {}

    # Method to clear the queue (if needed for other functionalities)
    def clear_queue(self, guild_id):
        if guild_id in self.song_queues:
            self.song_queues[guild_id] = asyncio.Queue()

    async def ensure_voice(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            await interaction.response.send_message("You need to be in a voice channel to play music.", ephemeral=True)
            return None
        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            # Connect to the voice channel if the bot is not connected
            try:
                voice_client = await voice_channel.connect()
            except discord.ClientException as e:
                logging.error(f"Failed to connect to voice channel: {e}")
                await interaction.response.send_message("Failed to connect to the voice channel.", ephemeral=True)
                return None
        elif voice_client.channel != voice_channel:
            # Move to the new voice channel if the bot is in a different channel
            try:
                await voice_client.move_to(voice_channel)
            except discord.ClientException as e:
                logging.error(f"Failed to move to a new voice channel: {e}")
                await interaction.response.send_message("Failed to move to the new voice channel.", ephemeral=True)
                return None

        # Start the voice status check as a background task
        self.bot.loop.create_task(self.check_voice_status(interaction.guild_id))
        return voice_client
    
    async def fetch_song_info(self, query):
        """
        Asynchronously searches for a song on YouTube and fetches comprehensive information about it.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'default_search': 'auto',
        }

        if not query.startswith("http"):
            query = f"ytsearch:{query}"

        try:
            # Execute the blocking operation in a separate thread to prevent blocking the event loop
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, query, download=False)

                # Handling playlists: select the first entry if it's a playlist
                if 'entries' in info:
                    info = info['entries'][0]

                return {
                    'title': info.get('title', 'Unknown Title'),
                    'thumbnail_url': info.get('thumbnail', None),
                    'uploader': info.get('uploader', 'Unknown Uploader'),
                    'duration': time.strftime('%H:%M:%S', time.gmtime(info.get('duration', 0))) if info.get('duration') else 'N/A',
                    'webpage_url': info.get('webpage_url', ''),
                    'url': info.get('url')  # Direct stream URL
                }
        except Exception as e:
            logging.error(f"Error fetching song info for '{query}': {e}")
            return None
        
    async def send_now_playing_embed(self, text_channel, voice_client, song_info, controls):
        """
        Sends an embed with now playing information to the text channel.
        """
        embed = discord.Embed(title="Now Playing", color=discord.Color.green())
        embed.add_field(name="Title", value=song_info.get('title', 'Unknown Title'), inline=False)

        duration = song_info.get('duration', 'N/A')
        embed.add_field(name="Duration", value=duration, inline=True)

        uploader = song_info.get('uploader', 'Unknown Uploader')
        embed.add_field(name="Uploader", value=uploader, inline=True)

        if thumbnail_url := song_info.get('thumbnail_url'):
            embed.set_thumbnail(url=thumbnail_url)

        embed.set_footer(text=f"Playing in {voice_client.channel.name}", icon_url=self.bot.user.display_avatar.url)
        
        if webpage_url := song_info.get('webpage_url'):
            embed.add_field(name="Link", value=webpage_url, inline=False)

        await text_channel.send(embed=embed, view=controls)

    async def download_song(self, query):
        """
        Downloads the song and returns the filename with extension.
        """
        timestamp = int(time.time())
        filename = f"downloads/song_{timestamp}.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            result = await ydl.download([query])
            if result != 0:
                logging.error("Error downloading the song.")
                return None
        return filename

    async def send_song_queued_embed(self, interaction, song_infos, controls):
        """
        Sends an embed with song queued information, handling multiple songs efficiently.
        """
        if not song_infos:
            logging.error("No song information provided to send_song_queued_embed.")
            return

        # If a single song info is passed, convert it to a list for uniform handling
        if isinstance(song_infos, dict):
            song_infos = [song_infos]

        # Initialize embed message
        embed = discord.Embed(title=":musical_note: Songs Queued", color=discord.Color.blue())
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # Add each song to the embed
        for song_info in song_infos:
            title = song_info.get('title', 'Unknown Title')
            duration = song_info.get('duration', 'N/A')
            uploader = song_info.get('uploader', 'Unknown Uploader')
            thumbnail_url = song_info.get('thumbnail_url')

            embed.add_field(name=title, value=f"Duration: {duration} | Uploader: {uploader}", inline=False)

            # Set thumbnail for the first song only to keep the embed clean
            if thumbnail_url and not embed.thumbnail:
                embed.set_thumbnail(url=thumbnail_url)

        # Send the embed message
        await interaction.followup.send(embed=embed, view=controls)
        
    @discord.app_commands.command(name="play", description="Play a YouTube video, Spotify playlist, or search for a video in the voice channel.")
    async def play_music(self, interaction: discord.Interaction, query: str):
        # Defer the interaction right away to prevent timeout
        await interaction.response.defer(thinking=True)

        if interaction.user.voice is None:
            await interaction.followup.send("You need to be in a voice channel to play music.", ephemeral=True)
            return

        voice_client = await self.ensure_voice(interaction)
        if not voice_client:
            await interaction.followup.send("Unable to join voice channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id
        self.command_channels[guild_id] = interaction.channel
        self.song_queues.setdefault(guild_id, asyncio.Queue())
        controls = MusicControls(self.bot, interaction)

        # Process Spotify playlist or single YouTube link
        if 'open.spotify.com/playlist/' in query:
            await self.process_spotify_playlist(interaction, query, guild_id)
        else:
            song_info = await self.fetch_song_info(query)
            if song_info:
                await self.song_queues[guild_id].put((song_info['url'], song_info, "stream"))
                await self.send_song_queued_embed(interaction, song_info, controls)
            else:
                await interaction.followup.send("Error: Could not retrieve song URL.", ephemeral=True)
                return

        # Start playing the song if nothing is playing
        if not voice_client.is_playing():
            await self.play_next_song(guild_id, controls=controls)

    async def process_spotify_playlist(self, interaction, query, guild_id):
        playlist_id = query.split('playlist/')[1].split('?')[0]
        spotify_tracks = await self.get_spotify_playlist_tracks(playlist_id)

        if not spotify_tracks:
            await interaction.followup.send("Could not fetch tracks from Spotify playlist.", ephemeral=True)
            return

        queued_songs = []
        for track in spotify_tracks:
            song_info = await self.fetch_song_info(track)
            if song_info:
                await self.song_queues[guild_id].put((song_info['url'], song_info, "stream"))
                queued_songs.append(song_info)

        if queued_songs:
            # Send an embed with the queued songs information
            embed = discord.Embed(title="Spotify Playlist Queued", color=discord.Color.green())
            for song in queued_songs:
                embed.add_field(name=song['title'], value=f"Duration: {song['duration']} - [Link]({song['webpage_url']})", inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("No tracks were added to the queue.", ephemeral=True)
            
    async def check_voice_status(self, guild_id, check_interval=15, grace_period=30):
        """Continuously check if the bot is alone or disconnected from the voice channel."""
        await asyncio.sleep(grace_period)  # Initial grace period
        while True:
            voice_client = self.bot.get_guild(guild_id).voice_client

            if voice_client and voice_client.is_connected():
                # Disconnect if the bot is the only member in the channel
                if len(voice_client.channel.members) == 1:
                    await voice_client.disconnect()
                    logging.info(f"Disconnected from voice channel in guild {guild_id} due to being alone.")
                    break
            else:
                # If disconnected, clean up and exit the loop
                self.command_channels.pop(guild_id, None)
                self.song_queues.pop(guild_id, None)
                logging.info(f"Voice client disconnected or not found in guild {guild_id}.")
                break

            await asyncio.sleep(check_interval)  # Wait before checking again


    async def play_next_song(self, guild_id, controls):
        voice_client = self.bot.get_guild(guild_id).voice_client

        if not voice_client or self.song_queues[guild_id].empty():
            logging.warning("No voice client or song queue is empty.")
            self.command_channels.pop(guild_id, None)
            return

        if not voice_client.is_connected():
            await self.attempt_reconnect(voice_client, guild_id, controls)
            return

        song_url, song_info, mode = await self.song_queues[guild_id].get()
        command_channel = self.command_channels.get(guild_id)
        if command_channel:
            await self.send_now_playing_embed(command_channel, voice_client, song_info, controls)

        try:
            # Adjust audio quality by modifying FFmpeg options
            audio_quality = "96k"  # Lower bitrate for reduced bandwidth usage
            voice_client.play(discord.FFmpegPCMAudio(song_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options=f"-bufsize 64k -b:a {audio_quality}"), after=lambda e: self.handle_playback_completion(e, guild_id, controls))
        except Exception as e:
            logging.error(f"Error playing song: {e}")
            if mode == "stream":
                filename = await self.download_song(song_info['webpage_url'])
                if filename:
                    await self.song_queues[guild_id].put((filename, song_info, "download"))
                    await self.play_next_song(guild_id, controls)


    def handle_playback_completion(self, error, guild_id, controls):
        if error:
            logging.error(f'Playback error: {error}')
        asyncio.run_coroutine_threadsafe(self.play_next_song(guild_id, controls), self.bot.loop)

    async def attempt_reconnect(self, voice_client, guild_id, controls):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if voice_client.is_connected():
                    await voice_client.disconnect()
                await asyncio.sleep(3)
                await voice_client.connect()
                break
            except Exception as e:
                logging.error(f"Reconnect attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logging.error("Max reconnect attempts reached. Giving up.")
                    return

        await self.play_next_song(guild_id, controls)


    async def get_spotify_token(self):
        """
        Get an access token for the Spotify API.
        """
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_header = {}
        auth_data = {}

        # Encode as Base64
        message = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        auth_header['Authorization'] = f"Basic {base64_message}"
        auth_data['grant_type'] = 'client_credentials'

        res = requests.post(auth_url, headers=auth_header, data=auth_data)
        token = res.json()['access_token']

        return token
    

    async def get_spotify_playlist_tracks(self, playlist_id):
        """
        Get the tracks from a Spotify playlist asynchronously, handling pagination.
        """
        token = await self.get_spotify_token()
        headers = {'Authorization': f'Bearer {token}'}
        playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'

        tracks = []
        async with aiohttp.ClientSession() as session:
            while playlist_url:
                try:
                    async with session.get(playlist_url, headers=headers) as response:
                        if response.status == 429:  # Rate limit hit
                            retry_after = int(response.headers.get("Retry-After", 1))
                            logging.info(f"Rate limited. Retrying after {retry_after} seconds.")
                            await asyncio.sleep(retry_after)
                            continue

                        if response.status != 200:
                            logging.error(f"Failed to fetch Spotify playlist: {response.status}")
                            break  # Exit the loop on failure

                        data = await response.json()
                        tracks.extend(
                            f"{item['track']['name']} by {item['track']['artists'][0]['name']}"
                            for item in data['items']
                        )

                        playlist_url = data.get('next')  # For handling pagination
                except aiohttp.ClientError as e:
                    logging.error(f"Failed to fetch Spotify playlist: {e}")
                    break  # Exit the loop on network error

        return tracks





async def setup(bot):
    music_cog = MusicCommands(bot)
    await bot.add_cog(music_cog)

    # Check if command is already registered before adding
    if not bot.tree.get_command('play'):
        await bot.tree.add_command(music_cog.play_music)
    await bot.tree.sync()
# Create a 'downloads' directory if it doesn't exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')