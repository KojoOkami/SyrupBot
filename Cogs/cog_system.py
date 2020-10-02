from discord.ext import commands

import config


class System(commands.Cog, name='System'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Signed in as ' + self.bot.user.display_name + "#" + self.bot.user.discriminator)
        print("Latency: " + str(int(self.bot.latency * 1000)) + "ms")

    @commands.command()
    async def latency(self, ctx):
        await ctx.send(str(int(self.bot.latency * 1000)) + "ms")