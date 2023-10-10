from discord.ext import commands
import os
import openai
import inspect

key = os.getenv("OPENAI_API_KEY")
openai.api_key = key


class AI(commands.Cog, name='AI'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='>', brief='Talk to the bot')
    async def talk(self, ctx, *, prompt=None):

        command_list = []
        for i in self.bot.commands:
            info = f"Command Name: {i} Brief: {i.brief} Long: {i.help} Category: {i.cog_name}"
            command_list.append(info)

        if prompt is None:
            await ctx.send('You need to say something!')
            return

        print(inspect.getmembers(ctx, lambda a: not (inspect.isroutine(a))))

        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=[
                                                    {"role": "system",
                                                     "content": "Your name is Rhythm and you are a discord bot. "
                                                                "You are trained to assist with a wide range of tasks."
                                                                "You are also trained to be a good conversationalist. "
                                                                "Help users by engaging in conversation and providing " 
                                                                "useful and relevant information. "
                                                                "This is metadata about the user content: "
                                                                f"{inspect.getmembers(ctx, lambda a: not (inspect.isroutine(a)))[12]}"
                                                                f"This is information about the bot's commands: "
                                                                f"{command_list}"
                                                                " When giving users this information, you should "
                                                                "just state the information without saying where you"
                                                                "got it from."},
                                                    {"role": "user", "content": prompt},
                                                ],
                                                temperature=.8,
                                                )
        await ctx.send(response["choices"][0]["message"]["content"])




async def setup(bot):
    await bot.add_cog(AI(bot))
