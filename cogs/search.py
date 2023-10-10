import discord
from discord.ext import commands
from scripts.google_search import *

class Search(commands.Cog, name='Search'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='search', brief='Search the web')
    async def search(self, ctx, *, arg=None):
        if arg is None:
            await ctx.send("Please provide a search query")
        else:
            results = get_results(arg)

            embed = discord.Embed(title=f"Google search results for '{arg}'", color=0x00ff00)
            if results["general"] != []:
                for i in results["general"]:
                    embed.add_field(name=i[1], value=f"[link]({i[3]})", inline=True)
            if results["top_stories"] != []:
                embed.add_field(name="Top Stories", value="", inline=False)
                for i in results["top_stories"]:
                    embed.add_field(name=i[0], value=f"[{i[1]}]({i[2]})", inline=True)

            embed.set_footer(text=f"Requested by {ctx.author.display_name} at {ctx.message.created_at.strftime('%H:%M:%S')}")
            await ctx.send(embed=embed)

    @commands.command(name='summary', brief='Uses AI to summarize news results')
    async def summary(self, ctx, *, arg=None):
        if arg is None:
            await ctx.send("Please provide a search query")
        else:
            results = get_news_results(arg)

            embed = discord.Embed(title=f"Summarized top news results for '{arg}'", color=0x00ff00)
            if results != []:
                embed.add_field(name="Top Stories", value="", inline=False)
                for i in results[:3]:
                    summary = summarize_url(i[2])
                    print(summary)
                    embed.add_field(name=i[0], value=f"[{summary}]({i[2]})", inline=False)
            else:
                embed.add_field(name="No results found", value="", inline=False)

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name} at {ctx.message.created_at.strftime('%H:%M:%S')}."
                     f"Summaries powered by AI from OpenAI")
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Search(bot))  # Add the Search cog to the bot
