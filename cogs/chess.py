from discord.ext import commands
import chess


class Chess(commands.Cog, name='Chess'):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name='start',
        brief='Starts a new chess game'
    )
    async def start(self, ctx):
        global board
        board = chess.Board()
        await ctx.send('New chess game started.')

    @commands.command(
        name='move',
        brief='Makes a move in the current chess game',
    )
    async def move(self, ctx, move: str):
        global board
        try:
            board.push_san(move)
            await ctx.send(f'Move {move} executed.')
            if board.is_game_over():
                await ctx.send(f"Game over. Result: {board.result()}")
        except ValueError:
            await ctx.send(f'Invalid move: {move}')

    @commands.command(
        name='show',
        brief='Shows the current board'
    )
    async def show(self, ctx):
        global board
        await ctx.send(f'```\n{board.unicode()}\n```')


async def setup(bot):
    await bot.add_cog(Chess(bot))
