from discord.ext import commands
from scripts.scripts_minigames import *


class MiniGames(commands.Cog, name='MiniGames'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='throw',
        brief='Rock Paper Scissors',
        description="Use the throw command, followed by 'rock', 'paper', or 'scissors'"
    )
    async def throw(self, ctx, arg=None):
        if arg is None:
            await ctx.send("Please provide an argument: 'rock', 'paper', or 'scissors'")
        else:
            await ctx.send(rps_game(arg))

    @commands.command(name='flip', brief='Flips a coin')
    async def flip(self, ctx):
        await ctx.send(coin_flip())


async def setup(bot):
    await bot.add_cog(MiniGames(bot))  # Add the Games cog to the bot
