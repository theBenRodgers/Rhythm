import discord
from discord.ext import commands
from scripts.bonka_chain import *
import time

def author_has_wallet():
    async def decorator(ctx):
        author = BonkaApp(ctx.author.id)
        if not author.wallet_exists():
            await ctx.send(f"You don't have a wallet yet <@{ctx.author.id}> Try >newwallet first!")
            return False
        return True
    return commands.check(decorator)


def is_admin():
    async def decorator(ctx):
        if ctx.author.id != 793879574580559882:
            await ctx.send(f"You can't do that")
            return False
        return True
    return commands.check(decorator)


def recipient_has_wallet():
    async def decorator(ctx):
        if not ctx.message.mentions:
            return False

        user = ctx.message.mentions[0]
        recipient = BonkaApp(user.id)
        if not recipient.wallet_exists():
            await ctx.send(f"<@{user.id}> does not have a wallet yet!")
            return False
        return True
    return commands.check(decorator)


class BonkaCoin(commands.Cog, name='BonkaCoin'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='newwallet', brief='Create a BonkaCoin wallet')
    async def newwallet(self, ctx):
        author = BonkaApp(ctx.author.id)
        if author.wallet_exists():
            await ctx.send('You already have a wallet!')
            return

        author.create_wallet()
        await ctx.send(f'You just opened a wallet <@{ctx.author.id}>')
        author.close_app()

    @commands.command(name='balance', brief='Show the world how poor you are')
    @author_has_wallet()
    async def balance(self, ctx):
        author = BonkaApp(ctx.author.id)
        await ctx.send(f"Balance: **{author.balance()}** Bonkas")
        author.close_app()

    @commands.command(name='pay', brief='No handouts allowed')
    @author_has_wallet()
    @recipient_has_wallet()
    async def pay(self, ctx, user: discord.Member, amount: int):
        if ctx.author.id == user.id:
            await ctx.send("You can't pay yourself")
            return

        author = BonkaApp(ctx.author.id)
        recipient = user.id

        if author.balance() < amount:
            ctx.sent("You don't have enough Bonkas")
            author.close_app()
            return

        bonkas = amount
        author.send_bonkas(recipient, bonkas)

        await ctx.send(f"<@{ctx.author.id}> sent <@{recipient}> **{amount}** Bonkas")
        author.close_app()

    @commands.command(name='mint', brief='Mints fresh BonkaCoin')
    @is_admin()
    @recipient_has_wallet()
    async def mint(self, ctx, user: discord.Member, amount: int):
        author = BonkaApp(ctx.author.id)
        recipient = user.id

        author.mint_bonkas(recipient, amount)

        await ctx.send(f"<@{recipient}> just got **{amount}** freshly minted Bonkas")
        author.close_app()

    @commands.command(name='destroy', brief='Protect against inflation')
    @is_admin()
    @recipient_has_wallet()
    async def destroy(self, ctx, user: discord.Member, amount: int):
        author = BonkaApp(ctx.author.id)
        recipient = user.id

        if BonkaApp(recipient).balance() < amount:
            ctx.sent(f"<@{recipient}> doesn't have enough Bonkas")
            author.close_app()
            return

        author.destroy_bonkas(recipient, amount)

        await ctx.send(f"<@{recipient}> just lost **{amount}** Bonkas")
        author.close_app()

    @commands.command(name='forbes', brief=r'The Bonkas 1%ers')
    async def forbes(self, ctx):
        author = BonkaApp(ctx.author.id)
        embed = discord.Embed(title='The Richest')
        current_time = time.ctime()
        c = 0
        for i in author.richest():
            c += 1
            user = self.bot.get_user(i[0])
            embed.add_field(name=f"{c}. {user.name}", value=f"{i[1]} Bonkas", inline=True)
        embed.set_footer(text=f"requested by {ctx.author.name} on {current_time}")
        await ctx.send(embed=embed)

        author.close_app()

    @commands.command(name='economy', brief=r'Economic info')
    async def economy(self,ctx):
        author = BonkaApp(ctx.author.id)

        current_time = time.ctime()
        c = 0
        bonkas = 0
        for i in author.economy():
            c += 1
            bonkas += i[0]

        embed = discord.Embed(title='Bonkas Economy', description=f"There are {bonkas} Bonkas circulating in {c} wallets.")
        embed.set_footer(text=f"requested by {ctx.author.name} on {current_time}")

        await ctx.send(embed=embed)

        author.close_app()

# TODO add more economy functionality

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
    
    """


async def setup(bot):
    await bot.add_cog(BonkaCoin(bot))
