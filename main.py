import discord
from discord.ext import commands
import yt_dlp as ytdlp  
import json
import re
import os



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

# play audio from YouTube (streaming only)
@bot.command()
async def play(ctx, * , query: str):
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


    # yt-dlp download options (streaming only)
         ydl_opts = {
            'format': 'bestaudio/best',  # Best quality 
            'noplaylist': True,          #  not playlists
            'quiet': True  ,              # Suppress yt-dlp output logs
            #'cookies': 'cookies.txt',
            'default_search': 'ytsearch1', 
          }
         await ctx.send(f"Bezar bebinam in gohi ke migi hast ya na")

         try:
             ydl = ytdlp.YoutubeDL(ydl_opts)
             info = ydl.extract_info(query, download=False)  # Extract video info 
            
            # (for search results)
             if 'entries' in info:
                stream_url = info['entries'][0]['url']  #  URL of the first search result
                title = info['entries'][0]['title']  #  video title
             else:
                stream_url = info['url']  # If it's a direct URL
                title = info['title']  #video title

         except Exception as e:
            await ctx.send(f"Error extracting information: {str(e)}")
            return
        

    else: 
        url = query
        ydl_opts = {
                'format' : 'bestaudio/best',
                'noplaylist' : True ,
                #'cookies': 'cookies.txt',
                'quiet' : True,
            }
        try:
            ydl = ytdlp.YoutubeDL(ydl_opts)
            info = ydl.extract_info(url, download=False)
            title = info['title']
            stream_url = info['url']
        except Exception as e:
            await ctx.send(f"Error extracting information from URL: {str(e)}")
            return


    if vc.is_playing():
        music_queue.append(stream_url)  # Add to queue if currently playing
        await ctx.send(f"Be queue add shod arbAb: {title}")
        return 

        # Play audio
    vc = ctx.voice_client
    vc.play(discord.FFmpegPCMAudio(stream_url), after=lambda e: print(f'Ahanget tamum shod Obi {title}'))

        #  buttons
    embed = discord.Embed(title=f'Khafe sho o goosh kon be: {title}', color=discord.Color.blue())
    embed.set_footer(text='Age nemidoni in button ha chi mikonan vaqean gaavi')

        #buttons
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
                await play(ctx, next_song)
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


#with open('config.json', 'r') as f:
 #   config = json.load(f)
#TOKEN = config['TOKEN']


TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("Error: DISCORD_TOKEN environment variable not set.")
else:
   
    bot.run(TOKEN)
