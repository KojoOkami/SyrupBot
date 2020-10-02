from discord.ext import commands

import functions as f
import config


class Staff(commands.Cog, name='Staff', command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if f.check_bot_role(message.author.roles):
            return
        await self.bot.get_channel(config.BOT_SYSTEM_CHANNEL_ID) \
            .send(content='message by ' + message.author.name + '#' + str(message.author.discriminator) +
                          ' deleted:```' + message.content + str([att.filename for att in message.attachments]) + '```')

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if f.check_bot_role(before.author.roles):
            return
        await self.bot.get_channel(config.BOT_SYSTEM_CHANNEL_ID) \
            .send(content=before.author.name + '#' + str(before.author.discriminator) +
                          ' edited message ' + str(before.id) + '.\nOld:```' + before.content +
                          str([att.filename for att in before.attachments]) + '```\nNow:```' + after.content +
                          str([att.filename for att in after.attachments]) + '```')
