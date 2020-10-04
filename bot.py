#!/usr/bin/env python3
from discord.ext import commands
import config

from Cogs.cog_system import System
from Cogs.cog_misc import Misc
from Cogs.cog_member import Member
from Cogs.cog_staff import Staff

bot = commands.Bot(command_prefix='!')

bot.add_cog(System(bot))
bot.add_cog(Misc(bot))
tempm = Member(bot)
bot.add_cog(tempm)
bot.add_cog(Staff(bot))

tempm.load_members()

bot.run(config.BOT_TOKEN)
