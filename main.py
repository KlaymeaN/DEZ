import discord
from discord.ext import commands
import yt_dlp as ytdlp  
import json

intents = discord.Intents.default()
intents.members = True



# Set up the bot and command prefix
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Command to join the voice channel
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not in a voice channel!")

# Command to leave the voice channel
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()

# Command to play audio from YouTube (streaming only)
@bot.command()
async def play(ctx, url: str):
    if not ctx.voice_client:  # If the bot isn't in a voice channel
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You are not in a voice channel!")
            return

    # yt-dlp download options (streaming only)
    ydl_opts = {
        'format': 'bestaudio/best',  # Best quality audio
        'noplaylist': True,          # Only process single video, not playlists
        'quiet': True                # Suppress yt-dlp output logs
    }

    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # Extract video info without downloading
        stream_url = info['url']                      # Get the direct audio URL
        
        # Play audio using FFmpeg
        vc = ctx.voice_client
        vc.play(discord.FFmpegPCMAudio(stream_url))







with open('config.json','r') as f:
    config = json.load(f)
TOKEN = config['TOKEN']

bot.run(TOKEN)
