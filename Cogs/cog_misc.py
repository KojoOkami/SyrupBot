from discord.ext import commands


class Misc(commands.Cog, name='Miscellaneous'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')
