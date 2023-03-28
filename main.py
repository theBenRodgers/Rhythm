import discord
from discord.ext import commands
from os import listdir
import json

INTENTS = discord.Intents.all()

file = open('config.json', 'r')
config = json.load(file)


actDict = config['ACTIVITY']
PREFIX = config['PREFIX']
TOKEN = config['TOKEN']
DESCRIPTION = config['DESCRIPTION']
CASE_INSENSITIVE = config['CASE_INSENSITIVE']

ACTIVITY = discord.Activity(type=discord.ActivityType.listening,
                            name=actDict['name'],
                            url=actDict['url'])

file.close()

#  Initialize the bot with the specified settings
bot = commands.Bot(intents=INTENTS,
                   command_prefix=PREFIX,
                   case_insensitive=CASE_INSENSITIVE,
                   activity=ACTIVITY,
                   description=DESCRIPTION)


@bot.event
async def on_ready():
    # Load all the cog files from the 'cogs/' directory
    for cog in listdir('cogs/'):
        if cog.endswith('.py'):
            await bot.load_extension(f'cogs.{cog[:-3]}')


bot.run(TOKEN)
