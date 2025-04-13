import discord
from discord.ext import commands
import yt_dlp
import asyncio

TOKEN = "MTIyNjM5ODkxMzEzMzY3NDU1OQ.GxBnsC.1pnU7a0lch1Q2ryTKKk0uk4RQTP309ys3LsPQE"
OWNER_ID = 1226398913133674559  # <-- Your Discord User ID

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

music_queues = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

# Join voice channel
@bot.command()
async def join(ctx):
    if ctx.author.id != OWNER_ID:
        return
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.message.delete()
    else:
        await ctx.send("❌ You must be in a voice channel.")

# Play command
@bot.command()
async def play(ctx, *, search: str):
    if ctx.author.id != OWNER_ID:
        return
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'ytsearch',
        'extract_flat': 'in_playlist',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        url = info['url']
        title = info.get('title', 'Unknown Title')

    guild_id = ctx.guild.id
    if guild_id not in music_queues:
        music_queues[guild_id] = []
    music_queues[guild_id].append((url, title, ctx))

    await ctx.send(f"🎶 Queued: **{title}**")
    if not ctx.voice_client.is_playing():
        await play_next(ctx)

async def play_next(ctx):
    guild_id = ctx.guild.id
    if music_queues[guild_id]:
        url, title, origin_ctx = music_queues[guild_id].pop(0)

        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)

        def after_playing(error):
            fut = play_next(ctx)
            fut = asyncio.run_coroutine_threadsafe(fut, bot.loop)
            try:
                fut.result()
            except:
                pass

        ctx.voice_client.play(source, after=after_playing)
        await origin_ctx.send(f"▶️ Now playing: **{title}**")

@bot.command()
async def skip(ctx):
    if ctx.author.id != OWNER_ID:
        return
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped.")
    else:
        await ctx.send("❌ Nothing is playing.")

@bot.command()
async def stop(ctx):
    if ctx.author.id != OWNER_ID:
        return
    guild_id = ctx.guild.id
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        music_queues[guild_id] = []
        await ctx.send("⏹️ Stopped and cleared.")
    else:
        await ctx.send("❌ Not connected.")

@bot.command()
async def leave(ctx):
    if ctx.author.id != OWNER_ID:
        return
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected.")
    else:
        await ctx.send("❌ Not connected.")

@bot.command()
async def queue(ctx):
    if ctx.author.id != OWNER_ID:
        return
    guild_id = ctx.guild.id
    if guild_id in music_queues and music_queues[guild_id]:
        msg = '\n'.join(f"{i+1}. {title}" for i, (_, title, _) in enumerate(music_queues[guild_id]))
        await ctx.send(f"📜 **Queue:**\n{msg}")
    else:
        await ctx.send("📭 Queue is empty.")

@bot.command(name="nowplaying")
async def now_playing(ctx):
    if ctx.author.id != OWNER_ID:
        return
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.send("🎵 Currently playing.")
    else:
        await ctx.send("❌ Nothing is playing.")

bot.run("MTIyNjM5ODkxMzEzMzY3NDU1OQ.GxBnsC.1pnU7a0lch1Q2ryTKKk0uk4RQTP309ys3LsPQE")
