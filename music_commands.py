import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os
import time
import logging

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

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queues = {}

    async def ensure_voice(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            await interaction.response.send_message("You need to be in a voice channel to play music.", ephemeral=True)
            return None
        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            return await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)
        return voice_client
    
    async def fetch_song_info(self, url):
        """
        Fetches comprehensive information about the song from YouTube.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': 'in_playlist',
            'default_search': 'auto'
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                # take first entry from a playlist
                info = info['entries'][0]

            return {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail_url': info.get('thumbnail', None),
                'uploader': info.get('uploader', 'Unknown Uploader'),
                'duration': time.strftime('%H:%M:%S', time.gmtime(info.get('duration', 0))) if info.get('duration') else 'N/A',
                'webpage_url': info.get('webpage_url', '')
            }

    async def send_now_playing_embed(self, text_channel, voice_client, song_info, controls):
        """
        Sends an embed with now playing information to the text channel.
        """
        embed = discord.Embed(title="Now Playing", color=discord.Color.green())
        embed.add_field(name="Title", value=song_info['title'], inline=False)
        embed.add_field(name="Duration", value=song_info['duration'], inline=True)
        embed.add_field(name="Uploader", value=song_info['uploader'], inline=True)
        if song_info.get('thumbnail_url'):
            embed.set_thumbnail(url=song_info['thumbnail_url'])
        embed.set_footer(text=f"Playing in {voice_client.channel.name}", icon_url=self.bot.user.display_avatar.url)
        if song_info.get('webpage_url'):
            embed.add_field(name="Link", value=song_info['webpage_url'], inline=False)

        await text_channel.send(embed=embed, view=controls)

    async def download_song(self, query, title):
        """
        Downloads the song and returns the filename with extension.
        """
        timestamp = int(time.time())
        filename = f"downloads/song_{timestamp}"

        if not os.path.exists('downloads'):
            os.makedirs('downloads')
            logging.info("Created 'downloads' directory.")

        ydl_opts_download = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': filename + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts_download) as ydl:
            result = ydl.download([query])
            if result != 0:
                logging.error(f"Error in downloading the song: {title}")
                return None

        return filename + '.mp3'

    async def send_song_queued_embed(self, interaction, song_info, controls):
        """
        Sends an embed with song queued information.
        """
        embed = discord.Embed(title=":musical_note: Song Queued", color=discord.Color.blue())
        embed.add_field(name="Title", value=song_info['title'], inline=False)
        embed.add_field(name="Duration", value=song_info['duration'], inline=True)
        embed.add_field(name="Uploader", value=song_info['uploader'], inline=True)
        if song_info['thumbnail_url']:
            embed.set_thumbnail(url=song_info['thumbnail_url'])
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed, view=controls)

    @discord.app_commands.command(name="play", description="Play a YouTube video or search for a video in the voice channel.")
    async def play_music(self, interaction: discord.Interaction, query: str):
        logging.info(f"Received play command with query: {query}")
        if interaction.user.voice is None:
            await interaction.response.send_message("You need to be in a voice channel to play music.", ephemeral=True)
            return

        voice_client = await self.ensure_voice(interaction)
        if not voice_client:
            await interaction.response.send_message("Unable to join voice channel.", ephemeral=True)
            return

        guild_id = interaction.guild_id
        self.song_queues.setdefault(guild_id, asyncio.Queue())

        if not query.startswith("http"):
            query = f"ytsearch:{query}"

        await interaction.response.send_message(f"Processing your request for `{query}`...", ephemeral=True)

        song_info = await self.fetch_song_info(query)
        filename_with_extension = await self.download_song(query, song_info['title'])
        if not filename_with_extension:
            await interaction.followup.send("Error in downloading the song.")
            return

        # Create an instance of MusicControls here
        controls = MusicControls(self.bot, interaction)

        await self.song_queues[guild_id].put((filename_with_extension, song_info))
        await self.send_song_queued_embed(interaction, song_info, controls)

        if not voice_client.is_playing():
            await self.play_next_song(guild_id, controls=controls)


    async def play_next_song(self, guild_id, controls):
        voice_client = self.bot.get_guild(guild_id).voice_client
        if not voice_client or self.song_queues[guild_id].empty():
            logging.warning("No voice client or song queue is empty.")
            return

        filename_with_extension, song_info = await self.song_queues[guild_id].get()

        if not os.path.isfile(filename_with_extension):
            logging.error(f"File not found for playback: {filename_with_extension}")
            return

        text_channel = voice_client.channel.guild.system_channel
        if text_channel:
            await self.send_now_playing_embed(text_channel, voice_client, song_info, controls)

        try:
            voice_client.play(discord.FFmpegPCMAudio(filename_with_extension), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(guild_id, controls), self.bot.loop))
        except Exception as e:
            logging.error(f"Error playing {filename_with_extension}: {e}")

        while voice_client is playing or voice_client.is_paused():
            await asyncio.sleep(1)

        os.remove(filename_with_extension)
                
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