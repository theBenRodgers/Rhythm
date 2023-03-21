from discord.ext import commands


class AI(commands.Cog, name='AI'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='>', brief='Talk to the bot')
    async def talk(self, ctx, arg=None):
        await ctx.send("Under development")


async def setup(bot):
    await bot.add_cog(AI(bot))
