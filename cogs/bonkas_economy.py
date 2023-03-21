import discord
from discord.ext import commands
from scripts.bonka_chain import *


class BonkaCoin(commands.Cog, name='BonkaCoin'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='newwallet', brief='Create a BonkaCoin wallet')
    async def newwallet(self, ctx):
        author = BonkaApp(int(ctx.author.id))
        if author.wallet_exists():
            await ctx.send('You already have a wallet!')
            return

        author.create_wallet()
        await ctx.send(f'You just opened a wallet <@{ctx.author.id}>')

    @commands.command(name='balance', brief='Show the world how poor you are')
    async def balance(self, ctx):
        author = BonkaApp(int(ctx.author.id))
        if not author.wallet_exists():
            await ctx.send(f"You don't have a wallet yet <@{ctx.author.id}> Try >newwallet first!")
            return

        await ctx.send(f"Balance: **{author.balance()}** Bonkas")

    @commands.command(name='pay', brief='No handouts allowed')
    async def pay(self, ctx, user: discord.Member, amount: int):
        author = BonkaApp(int(ctx.author.id))
        if not author.wallet_exists():
            await ctx.send(f"You don't have a wallet yet <@{ctx.author.id}> Try >newwallet first!")
            return

        recipient = int(user.id) # TODO check if recipient exists (you need to make decorators i stg bro dont fuck me
                                # TODO also get that control flow shit out the app, do that here

        bonkas = amount

        author.send_bonkas(recipient, bonkas)

        await ctx.send(f"@<{ctx.author.id}> sent @<{recipient}> **{amount}** Bonkas")

    @commands.command(name='mint', brief='Mints fresh BonkaCoin')
    async def mint(self, ctx, user: discord.Member, amount: int):
        author = BonkaApp(int(ctx.author.id))
        if ctx.author.id != 793879574580559882:
            await ctx.send(f"You can't do that")
            return
        if not author.wallet_exists():
            await ctx.send(f"You don't have a wallet yet <@{ctx.author.id}> Try >newwallet first!")
            return

        recipient = int(user.id)
        author.mint_bonkas(recipient, amount)

    @commands.command(name='destroy', brief='Protect against inflation')
    async def destroy(self, ctx, user: discord.Member, amount: int):
        author = BonkaApp(int(ctx.author.id))
        if ctx.author.id != 793879574580559882:
            await ctx.send(f"You can't do that")
            return
        if not author.wallet_exists():
            await ctx.send(f"You don't have a wallet yet <@{ctx.author.id}> Try >newwallet first!")
            return

        recipient = int(user.id)
        author.destroy_bonkas(recipient, amount)

# TODO add more econonomy functionality
""" 
    @commands.command(name='shop', brief='Consuuuuuuuume')
    async def shop(self, ctx):
        await ctx.send('Shop')

    @commands.command(name='work', brief='Get a job you filthy poor')
    async def work(self, ctx):
        await ctx.send('Work')

    @commands.command(name='rob', brief='Bonkas don\'t grow on trees')
    async def rob(self, ctx, user: discord.Member):
        await ctx.send('Rob')
        
    @commands.command(name='daily', brief='Get "free" Bonkas every day')
    async def daily(self, ctx):
        await ctx.send('Daily')

    @commands.command(name='forbes', brief=r'The Bonkas 1%ers')
    async def forbes(self, ctx):
        await ctx.send('Forbes')
      """

async def setup(bot):
    await bot.add_cog(BonkaCoin(bot))
