from discord.ext import commands


class Misc(commands.Cog, name='Miscellaneous'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command(hidden=True)
    async def pong(self, ctx):
        if ctx.author.id == 688917542378537024:
            await ctx.send(ctx.author.mention)
