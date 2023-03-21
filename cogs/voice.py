import discord
from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from scripts.yt import downloader


class Voice(commands.Cog, name='Voice'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join', brief='Joins your voice channel')
    async def join(self, ctx):
        user = ctx.author  # Get the user who sent the command
        
        # Check if the user is connected to a voice channel
        if not user.voice:
            await ctx.send("Join a channel first")
            return

        channel = user.voice.channel  # Get the voice channel of the user
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        # Check if the bot is not in a voice channel
        if not voice:
            await channel.connect()
            await ctx.send(f"Joined **{channel}**")
        # Check if the bot and user are already in the same voice channel
        elif ctx.bot.user in channel.members:
            await ctx.send(f"I'm already in **{channel}**")
        # If the bot is in another voice channel, move it to the user's channel
        else:
            await ctx.guild.voice_client.move_to(channel)
            await ctx.send(f"Moved to **{channel}**")

    @commands.command(name='leave', brief='Leaves voice channel')
    async def leave(self, ctx):
        # Check if the bot is in a voice channel
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.send('Bot left')
        # If the bot is not in a voice channel, inform the user
        else:
            await ctx.send("I'm not in a voice channel, use the join command to make me join")

    @commands.command(name='play', brief='Plays a song')
    async def play(self, ctx, url):
        # Check if the user is connected to a voice channel
        if not ctx.author.voice:
            await ctx.send("Join a channel first")
            return
        
        # If bot and user are not in the same voice channel already, invoke join command
        if ctx.bot.user not in ctx.author.voice.channel.members:
            await ctx.invoke(self.join)

        # Check if the url is valid
        if not url.startswith('https://www.youtube.com/watch?v='):
            await ctx.send("Invalid URL")
            return
        
        # download and play audio file
        audio = downloader(url)
        ctx.voice_client.play(FFmpegPCMAudio(str(audio)), after=lambda e: print('done', e))
        ctx.voice_client.source = PCMVolumeTransformer(ctx.voice_client.source)
        ctx.voice_client.source.volume = 0.07

    @commands.command(name='pause', brief='Pauses the song')
    async def pause(self, ctx):
        await ctx.send('Under Development')

    @commands.command(name='queue', brief='Shows the queue')
    async def queue(self, ctx):
        await ctx.send('Under Development')

    @commands.command(name='skip', brief='Skips the song')
    async def skip(self, ctx):
        await ctx.send('Under Development')

    @commands.command(name='stop', brief='Stops the song')
    async def stop(self, ctx):
        await ctx.send('Under Development')

    @commands.command(name='song', brief='Shows the current song')
    async def song(self, ctx):
        await ctx.send('Under Development')

    @commands.command(name='volume', brief='Changes the volume')
    async def volume(self, ctx, volume):
        await ctx.send('Under Development')
    

async def setup(bot):
    await bot.add_cog(Voice(bot))  # Add the Voice cog to the bot
