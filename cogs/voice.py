import asyncio
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from scripts.yt import *
from scripts.musicqueue import *
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

        if not hasattr(ctx, "auto_play"):
            ctx.auto_play = False



        async def play_from_queue(guild):
            bot_voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            serverq = MusicQueue(guild)
            if not bot_voice:
                serverq.close_queue()
                return

            if not serverq.does_queue_exist():
                await ctx.guild.voice_client.disconnect()
                await ctx.send("Nothing left to play. Bot left")
                serverq.close_queue()
                return


            next_item = serverq.get_next_song()
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
            await ctx.send(embed=embed)

            serverq.remove_now_playing()
            serverq.update_now_playing(time_stamp)

            while ctx.voice_client.is_playing():
                await asyncio.sleep(.1)
            os.remove(path)

            serverq.remove_song(time_stamp)

            if serverq.does_queue_exist() and ctx.voice_client.is_connected():
                await ctx.invoke(self.bot.get_command("play"), auto_play=True)
                serverq.close_queue()
                return

            if not serverq.does_queue_exist() and ctx.voice_client.is_connected():
                await ctx.guild.voice_client.disconnect()
                await ctx.send("Nothing left to play. Bot left")
                serverq.close_queue()
                return

            serverq.close_queue()
            return

        # Runs if the command was invoked
        if ctx.auto_play:
            bot_voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if not bot_voice:
                return
            if ctx.voice_client.is_playing():
                return

            await play_from_queue(ctx.voice_client.guild.id)

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

        serverq = MusicQueue(ctx.message.guild.id)

        if prompt == "":
            if ctx.voice_client.is_playing():
                await ctx.send("Already playing!")
                serverq.close_queue()
                return
            if not serverq.does_queue_exist():
                await ctx.send("Nothing left to play, pick a song!")
                serverq.close_queue()
                return
            serverq.close_queue()

            await play_from_queue(ctx.message.guild.id)
            return

        time_stamp = datetime.datetime.now().timestamp() * 100
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
        else:
            url = prompt

        title = title_from_url(url)

        serverq = MusicQueue(ctx.message.guild.id)

        if ctx.voice_client.is_playing():  # Adds the song to the queue if the bot is already playing audio
            to_add = (ctx.message.guild.id, title, url, ctx.author.id, time_stamp, 0)
            serverq.add_to_queue(to_add)
            serverq.close_queue()

            await ctx.send(f"{title} has been added to the queue", delete_after=10)

            if bot_msg:
                await bot_msg.delete()
            return

        to_add = (ctx.message.guild.id, title, url, ctx.author.id, time_stamp, 1)

        print(to_add)

        serverq.add_to_queue(to_add)


        path = download_audio(url, str(ctx.message.guild.id), str(ctx.author.id))
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable=r"C:\ffmpeg\bin\ffmpeg.exe", source=path))
        ctx.voice_client.source = PCMVolumeTransformer(ctx.voice_client.source)

        embed = discord.Embed(title="Now Playing", description=f"[{title}]({url})", color=0xE74C3C)
        embed.set_thumbnail(url=get_thumbnail_url(url))
        embed.set_footer(text=f"Added by {user}")
        await ctx.send(embed=embed)

        while ctx.voice_client.is_playing():
            await asyncio.sleep(.1)
        os.remove(path)

        serverq.remove_song(time_stamp)
        serverq.close_queue()

        await play_from_queue(ctx.message.guild.id)

    @commands.command(name='queue', brief='Shows the queue', )
    async def queue(self, ctx, page=1):
        serverq = MusicQueue(ctx.message.guild.id)
        q = serverq.get_all_songs()

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

        serverq.close_queue()

    @commands.command(name='song', brief='Shows the current song')
    async def song(self, ctx):
        serverq = MusicQueue(ctx.message.guild.id)

        playing = serverq.get_now_playing()

        serverq.close_queue()

        if not playing:
            await ctx.send("Nothing is playing")
            return

        title = playing[1]
        url = playing[2]
        user = self.bot.get_user(playing[3]).name

        embed = discord.Embed(title="Now Playing", description=f"[{title}]({url})", color=0xE74C3C)
        embed.set_thumbnail(url=get_thumbnail_url(url))
        embed.set_footer(text=f"Added by {user}")
        await ctx.send(embed=embed)

    @commands.command(name='clearq', brief='Clears the queue')
    async def clearq(self, ctx):
        serverq = MusicQueue(ctx.message.guild.id)

        serverq.clear_queue()

        await ctx.send("Queue has been cleared")

        serverq.close_queue()

    @commands.command(name='skip', brief='Skips the song')
    async def skip(self, ctx):
        await ctx.send('Under Development')

    @commands.command(name='stop', brief='Stops the song')
    async def stop(self, ctx):
        await ctx.send('Under Development')

async def setup(bot):
    await bot.add_cog(Voice(bot))  # Add the Voice cog to the bot
