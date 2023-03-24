import asyncio
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from scripts.yt import *
from scripts.queue import *
import os
import datetime


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
    async def play(self, ctx, *, prompt=""):

        if prompt == "":
            if not ctx.voice_client.is_playing():
                serverq = Queue(ctx.voice_client.guild.id)
                if not serverq.queue_exists():
                    await ctx.send("Nothing in queue, pick a song for me to play")

                if ctx.voice_client and len(ctx.voice_client.channel.members) == 1:  # If bot is only one in channel
                    await ctx.guild.voice_client.disconnect()
                    await ctx.send("Bot left due to inactivity")
                    return

                next_item = serverq.queue_next()
                time_stamp = next_item[4]
                url = next_item[2]
                user = self.bot.get_user(next_item[3]).name
                title = next_item[1]

                path = download_audio(url, str(ctx.message.guild.id), str(ctx.author.id))
                ctx.voice_client.play(discord.FFmpegPCMAudio(executable=r"C:\ffmpeg\bin\ffmpeg.exe", source=path))
                ctx.voice_client.source = PCMVolumeTransformer(ctx.voice_client.source)

                embed = discord.Embed(title="Now Playing", description=f"[{title}]({url})", color=0xE74C3C)
                embed.set_thumbnail(url=get_thumbnail_url(url))
                embed.set_footer(text=f"Added by {user}")
                bot_msg = await ctx.send(embed=embed)

                serverq.set_now_playing(time_stamp)

                while ctx.voice_client.is_playing():
                    await asyncio.sleep(.1)
                os.remove(path)

                serverq.queue_remove(time_stamp)

                if serverq.queue_exists() and ctx.voice_client.is_connected():
                    await ctx.invoke(self.bot.get_command("play"), prompt="from_queue")
                    serverq.queue_close()
                    return
                else:
                    await ctx.guild.voice_client.disconnect()
                    await ctx.send("Nothing left to play. Bot left")
                    serverq.queue_close()
                return
            else:
                await ctx.send("Already playing!")
                return

        bot_msg = None  # Sets variable to None to check if choice prompt was run
        user = ctx.author  # Get the user who sent the command

        if not user.voice:  # Check if the user is connected to a voice channel
            await ctx.send("Join a channel first")
            return
        channel = user.voice.channel  # Get the voice channel of the user
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:  # Check if the bot is not in a voice channel
            await channel.connect()
        elif ctx.bot.user in channel.members:  # Check if the bot and user are already in the same voice channel
            pass
        else:  # If the bot is in another voice channel, move it to the user's channel
            await ctx.guild.voice_client.move_to(channel)
        time_stamp = datetime.datetime.now().timestamp()*100
        time_stamp = int(round(time_stamp))

        prompt = prompt.strip()  # Removes any extra spaces

        if not prompt.startswith("https://www.youtube.com/watch?v="):  # Searches for prompt if not YouTube url
            results = youtube_search_results(prompt)
            embed = discord.Embed(title=f"Search results for {prompt}:", description="Select a result")
            for index, element in enumerate(results):
                embed.add_field(name=f"{index+1}", value=f"{results[index][0]}", inline=True)

            bot_msg = await ctx.send(embed=embed, delete_after=30)

            def check(m):
                return (
                    m.channel.id == ctx.channel.id
                    and m.content == "1"
                    or m.content == "2"
                    or m.content == "3"
                    or m.content.startswith(">play")
                )
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
                if msg:
                    if msg.content.startswith(">play"):
                        await bot_msg.delete()
                        return
                    if msg.content == "1":
                        url = results[0][1]
                    elif msg.content == "2":
                        url = results[1][1]
                    elif msg.content == "3":
                        url = results[2][1]
            except asyncio.TimeoutError:
                await bot_msg.delete()
                await ctx.send("Choice timed out", delete_after=15)
                return

        title = title_from_url(url)

        serverq = Queue(ctx.message.guild.id)

        if ctx.voice_client.is_playing():  # Adds the song to the queue if the bot is already playing audio
            to_add = (ctx.message.guild.id, title, url, ctx.author.id, time_stamp, int(0))
            serverq.queue_add(to_add)
            serverq.queue_close()

            await ctx.send(f"{title} has been added to the queue", delete_after=10)

            if bot_msg:
                await bot_msg.delete()
            return

        to_add = (ctx.message.guild.id, title, url, ctx.author.id, time_stamp, int(1))

        serverq.queue_add(to_add)
        serverq.queue_close()

        path = download_audio(url, str(ctx.message.guild.id), str(ctx.author.id))
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable=r"C:\ffmpeg\bin\ffmpeg.exe", source=path))
        ctx.voice_client.source = PCMVolumeTransformer(ctx.voice_client.source)

        if bot_msg:
            await bot_msg.delete()

        embed = discord.Embed(title="Now Playing", description=f"[{title}]({url})", color=0xE74C3C)
        embed.set_thumbnail(url=get_thumbnail_url(url))
        embed.set_footer(text=f"Added by {user}")
        await ctx.send(embed=embed)

        while ctx.voice_client.is_playing():
            await asyncio.sleep(.1)
        await bot_msg.delete()
        os.remove(path)

        serverq = Queue(ctx.message.guild.id)
        serverq.queue_clear(time_stamp)


        if serverq.queue_exists() and ctx.voice_client.is_connected():
            await ctx.invoke(self.bot.get_command("play"), prompt="")
        if not serverq.queue_exists() and ctx.voice_client.is_connected():
            await ctx.guild.voice_client.disconnect()
            await ctx.send("Nothing left to play. Bot left")

        serverq.queue_close()

    @commands.command(name='queue', brief='Shows the queue', )
    async def queue(self, ctx, page=1):
        serverq = Queue(ctx.message.guild.id)
        q = serverq.queue_all()

        if not q:
            await ctx.send("Nothing queued")
            return
        items_per_page = 5
        items = len(q)
        incomplete_page = items % items_per_page

        if incomplete_page == 0:
            pages = items / items_per_page
        else:
            pages = items // items_per_page + 1

        if page > pages:
            page = pages
        if page < 1:
            page = 1

        if page == pages:
            last_index = page * items_per_page - (items_per_page - incomplete_page)
            first_index = last_index - incomplete_page
        else:
            last_index = page * items_per_page
            first_index = last_index - items_per_page

        embed = discord.Embed(title="Queue")

        for count, item in enumerate(q[first_index: last_index]):
            number = count + first_index + 1
            title = item[1]
            url = item[2]
            user = self.bot.get_user(item[3]).name
            embed.add_field(name=f"[{number}] {title}", value=f"Added by {user}", inline=False)

        embed.set_footer(text=f"Page [{page}/{int(pages)}]")

        await ctx.send(embed=embed)

        serverq.queue_close()

    @commands.command(name='song', brief='Shows the current song')
    async def song(self, ctx):
        serverq = Queue(ctx.message.guild.id)

        playing = serverq.now_playing()

        title = playing[1]
        url = playing[2]
        user = self.bot.get_user(playing[3]).name

        embed = discord.Embed(title="Now Playing", description=f"[{title}]({url})", color=0xE74C3C)
        embed.set_thumbnail(url=get_thumbnail_url(url))
        embed.set_footer(text=f"Added by {user}")
        await ctx.send(embed=embed)

    @commands.command(name='clearq', brief='Clears the queue')
    async def clearq(self, ctx):
        serverq = Queue(ctx.message.guild.id)

        serverq.queue_clear()

        await ctx.send("Queue has been cleared")

        serverq.queue_close()

    @commands.command(name='skip', brief='Skips the song')
    async def skip(self, ctx):
        await ctx.send('Under Development')

    @commands.command(name='stop', brief='Stops the song')
    async def stop(self, ctx):
        await ctx.send('Under Development')

async def setup(bot):
    await bot.add_cog(Voice(bot))  # Add the Voice cog to the bot
