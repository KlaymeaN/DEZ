import discord
from discord.ext import commands
import yt_dlp as ytdlp
import json
import read 
import os
import shutil
import re 

print("opus loaded: ", discord.opus.is_loaded())



intents = discord.Intents.default()
intents.members = True
intents.voice_states = True  # Required for voice channel features
intents.messages = True  #  read message
intents.message_content = True



# Set up the bot and command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# store the current voice client and queue
music_queue = []





def is_url(input_str):
    #  if the input is a URL
    url_regex = re.compile(r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$')
    return bool(url_regex.match(input_str))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# join
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Oomadam Soraghet tu channel e  {channel.name}, Police makhfi!")
    else:
        await ctx.send("Koskhol aval bayad tu channel bashi")

# leave
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Ta doroodi digar, bedrood")
    else:
        await ctx.send("Tu voice channel nistam ahmaq")


# no streaming
@bot.command()
async def play(ctx, *, query: str):
    if not ctx.voice_client:  # If the bot isn't in a voice channel
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"Kos o Kooneto jam kon az {channel.name}")
        else:
            await ctx.send("Tu channel nisti ke! to khode khari")
            return

    vc = ctx.voice_client

    if not is_url(query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch1',
            'outtmpl': '%(title)s.%(ext)s',  # Save the audio file with the video title
            
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        await ctx.send(f"Bezar bebinam in gohi ke migi hast ya na")
        try:
            ydl = ytdlp.YoutubeDL(ydl_opts)
            info = ydl.extract_info(query, download=True)  # Download the audio file

            # (for search results)
            if 'entries' in info:
                audio_file = info['entries'][0]['title'] + '.mp3'
                title = info['entries'][0]['title']
            else:
                audio_file = info['title'] + '.mp3'
                title = info['title']

        except Exception as e:
            await ctx.send(f"Error extracting information: {str(e)}")
            return

    else:
        url = query
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'outtmpl': '%(title)s.%(ext)s',
            
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        try:
            ydl = ytdlp.YoutubeDL(ydl_opts)
            info = ydl.extract_info(url, download=True)
            audio_file = info['title'] + '.mp3'
            title = info['title']
        except Exception as e:
            await ctx.send(f"Error extracting information from URL: {str(e)}")
            return

    if vc.is_playing():
        music_queue.append(audio_file)  # Add to queue if currently playing
        await ctx.send(f"Be queue add shod arbAb: {title}")
        return

    # Play audio from the downloaded file
    vc = ctx.voice_client
    vc.play(discord.FFmpegOpusAudio(audio_file), after=lambda e: os.remove(audio_file))

    # Rest of the code remains the same

    # buttons
    embed = discord.Embed(title=f'Khafe sho o goosh kon be: {title}', color=discord.Color.blue())
    embed.set_footer(text='Age nemidoni in button ha chi mikonan vaqean gaavi')

    # buttons
    play_button = discord.ui.Button(label="Play", style=discord.ButtonStyle.primary)
    pause_button = discord.ui.Button(label="Pause", style=discord.ButtonStyle.secondary)
    skip_button = discord.ui.Button(label="Skip to next", style=discord.ButtonStyle.success)

    # Define button interactions
    async def play_callback(interaction):
        if vc.is_paused():
            vc.resume()
            await interaction.response.send_message('Resume kardam', ephemeral=True)

    async def pause_callback(interaction):
        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message('Mage man allafe toam?', ephemeral=True)

    async def skip_callback(interaction):
        if music_queue:
            next_song = music_queue.pop(0)
            vc.stop()
            os.remove(audio_file)  # Remove the previous audio file
            await play(ctx, query=next_song)
            await interaction.response.send_message(f'Skip shod be: {next_song}', ephemeral=True)
        else:
            await interaction.response.send_message('Bi shOoor, chizi tu queue nist ke', ephemeral=True)

    play_button.callback = play_callback
    pause_button.callback = pause_callback
    skip_button.callback = skip_callback

    # buttons
    view = discord.ui.View()
    view.add_item(play_button)
    view.add_item(pause_button)
    view.add_item(skip_button)

    # buttons
    await ctx.send(embed=embed, view=view)


#  stop playback
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Mano Stop mikoni bache kooni?")
    else:
        await ctx.send("Tu channel nistam ke oksol")


#playlist


def load_playlists():
    if os.path.exists('playlists.json'):
        with open('playlists.json','r') as file:
            return json.load(file)
    return {}

def save_playlists(playlists):
    with open('playlists.json', 'w') as file:
        json.dump(playlists, file, indent=4)

def add_song_to_playlist(playlist_name, song):
    playlists = load_playlists()
    if playlist_name not in playlists:
        playlists[playlist_name] = []
    playlists[playlist_name].append(song)
    save_playlists(playlists)









# Playlist command
@bot.command()
async def playlist(ctx, action: str, playlist_name: str, *, song: str = None):
    playlists = load_playlists()

    if action.lower() == "create":
        if playlist_name in playlists:
            await ctx.send(f"Playlist `{playlist_name}` already exists!")
        else:
            playlists[playlist_name] = []
            save_playlists(playlists)
            await ctx.send(f"Playlist `{playlist_name}` created successfully.")

    elif action.lower() == "add":
        if not song:
            await ctx.send("Please specify a song to add!")
            return

        if playlist_name in playlists:
            add_song_to_playlist(playlist_name, song)
            await ctx.send(f"Added `{song}` to playlist `{playlist_name}`.")
        else:
            await ctx.send(f"Playlist `{playlist_name}` does not exist. Use `!playlist create {playlist_name}` first.")

    elif action.lower() == "play":
        if playlist_name in playlists:
            if not playlists[playlist_name]:
                await ctx.send(f"Playlist `{playlist_name}` is empty.")
                return

            # Play the first song in the playlist
            for song in playlists[playlist_name]:
                await play(ctx, query=song)  # Reuse the play command
            await ctx.send(f"Finished playing playlist `{playlist_name}`.")
        else:
            await ctx.send(f"Playlist `{playlist_name}` does not exist.")
    
    elif action.lower() == "list":
        if playlist_name in playlists:
            songs = playlists[playlist_name]
            if songs:
                song_list = '\n'.join(songs)
                await ctx.send(f"Songs in `{playlist_name}`:\n{song_list}")
            else:
                await ctx.send(f"Playlist `{playlist_name}` is empty.")
        else:
            await ctx.send(f"Playlist `{playlist_name}` does not exist.")
    else:
        await ctx.send("Invalid action. Use `create`, `add`, `play`, or `list`.")




#HELP
@bot.command()
async def komak(ctx):
    help_messages = """
    **Commands:**
    - 'play' : - Plays Yt link or query 
    - 'stop' : - Stops
    - 'playlist play <name>' : - Plays an existing playlist
    - 'playlist list <name>' : - lists songs of a playlist
    - 'playlist create <name> ' : - Creates new playlist
    - 'playlist add <name> <song> ' : - adds song to playlist



    """
    await ctx.send(help_messages)

















try:
    with open('config.json', 'r') as f:
       config = json.load(f)
    TOKEN = config['TOKEN']
except:
    print("config file not found reading token from env")
    TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("Error: DISCORD_TOKEN environment variable not set.")
else:

    bot.run(TOKEN)

