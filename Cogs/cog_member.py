from discord.ext import commands
import discord.utils

import enum
from os import listdir
from os.path import isfile, join
import json

import functions as f
import config

members = {}


class Ranks(enum.Enum):
    lurker = {
        'index': 0,
        'name': 'Lurker',
        'divisions': 1,
        'ap': [0],
        'role_id': '740391682633367683'
    }
    member = {
        'index': 1,
        'name': 'Member',
        'divisions': 5,
        'ap': [100, 200, 300, 400, 500],
        'role_id': '740391683748921396'
    }
    known = {
        'index': 2,
        'name': 'Known',
        'divisions': 5,
        'ap': [800, 1100, 1400, 1700, 2000],
        'role_id': '740391684604428298'
    }
    regular = {
        'index': 3,
        'name': 'Regular',
        'divisions': 5,
        'ap': [3000, 4000, 5000, 6000, 7000],
        'role_id': '740391685166727180'
    }
    hero = {
        'index': 4,
        'name': 'Hero',
        'divisions': 3,
        'ap': [10000, 13000, 16000],
        'role_id': '740391685887885360'
    }
    legend = {
        'index': 5,
        'name': 'Legend',
        'divisions': 3,
        'ap': [22000, 28000, 34000],
        'role_id': '740391686991118476'
    }
    master = {
        'index': 6,
        'name': 'Master',
        'divisions': 1,
        'ap': [50000],
        'role_id': '740391687385514046'
    }
    syrup_phoenix = {
        'index': 7,
        'name': 'Syrup Phoenix',
        'divisions': 1,
        'ap': [100000],
        'role_id': '740391688215855114'
    }


rank_list = [Ranks.lurker, Ranks.member, Ranks.known, Ranks.regular, Ranks.hero, Ranks.legend, Ranks.master,
             Ranks.syrup_phoenix]


class Divisions(enum.Enum):
    phoenix = "『✸』"
    master = "『★』"
    one = "『Ⅰ』"
    two = "『Ⅱ』"
    three = "『Ⅲ』"
    four = "『Ⅳ』"
    five = "『Ⅴ』"


def get_division_by_number(num):
    nums = [Divisions.one, Divisions.two, Divisions.three, Divisions.four, Divisions.five]
    return nums[num]


class Achievements(enum.Enum):
    pog = {
        'name': 'Pog!',
        'index': 0
    }
    winged = {
        'name': 'Winged',
        'index': 1
    }


class Member(commands.Cog, name='Member'):
    def __init__(self, bot):
        self.bot = bot
        self.rank_roles = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.author) is not discord.User:
            if f.check_bot_role(message.author.roles):
                return
        await self.increase_ap(self.get_member_by_id(message.author.id), await f.value_message(message))

    @commands.command()
    async def rank(self, ctx):
        syrupmember = self.get_member_by_id(ctx.author.id)
        nick = syrupmember.nick
        if nick is None:
            nick = ctx.author.name
        values = await self.check_ap(syrupmember)
        percent = float(values[1] - values[0]) / float(values[2] - values[0])
        bars = int(percent * 15)
        display_bars = '['
        for i in range(bars):
            display_bars += '■'
        for i in range(15 - bars):
            display_bars += '-'
        display_bars += ']'
        await ctx.message.channel.send('**' + nick + '**\n---------------\n' + syrupmember.rank.value['name'] +
                                       get_division_by_number(syrupmember.division-1).value + '\n' +
                                       display_bars)

    @commands.command(name='checkap', hidden=True)
    async def check_all_ap(self, ctx):
        if f.check_admin(ctx.author.roles):
            print('Checking member ap')
            for member in members:
                await self.increase_ap(self.get_member_by_id(member), 0)
            print('Done!')

    @commands.command(name='recalc', hidden=True)
    async def recalculate_rank(self, ctx):
        if f.check_admin(ctx.author.roles):
            print('Recalculating user AP')
            users = {}
            for t_channel in ctx.guild.text_channels:
                print('Getting history for Text Channel: ' + t_channel.name)
                last_message = None
                async for message in t_channel.history(limit=None, oldest_first=True):
                    member = message.author
                    if type(member) is not discord.User:
                        if not f.check_bot_role(member.roles):
                            if str(member.id) not in users:
                                users[str(member.id)] = 0
                            users[str(member.id)] += await f.value_message(message, last_message=last_message)
                            last_message = message
            print('Assigning AP to Users')
            for user in users:
                await self.set_ap(self.get_member_by_id(int(user)), users[user])
            print('Done!')

    ###
    # Syrup Member Management
    ###

    class SyrupMember:
        """
        Vars:

        user_id - string
        rank - String
        division - int
        ap - int
        nick - string
        achievements - tuple of booleans
        """

        def __init__(self, user_id, rank: Ranks = None, division: int = 0, ap: int = 0, nick: str = None,
                     achievements: tuple = None):
            if type(user_id) is dict:
                self.user_id = user_id['user_id']
                self.rank = rank_list[int(user_id['rank'])]
                self.division = user_id['division']
                self.ap = user_id['ap']
                self.nick = user_id['nick']
                self.achievements = user_id['achievements']
            else:
                self.user_id = int(user_id)
                if rank is None:
                    self.rank = Ranks.lurker
                else:
                    self.rank = rank
                self.division = division
                self.ap = ap
                self.nick = nick
                if achievements is None:
                    self.achievements = []
                else:
                    self.achievements = achievements
            members[self.user_id] = self

        def set_achievement(self, achievement: Achievements):
            self.achievements[achievement.value['index']] = True

        def to_dict(self):
            return {
                'user_id': self.user_id,
                'rank': self.rank.value['index'],
                'division': self.division,
                'ap': self.ap,
                'nick': self.nick,
                'achievements': self.achievements
            }

    async def increase_ap(self, member: SyrupMember, amount: int):
        if member.ap is None:
            member.ap = 0
        member.ap += amount
        await self.check_ap(member)

    async def set_ap(self, member: SyrupMember, amount: int):
        member.ap = amount
        await self.check_ap(member)

    async def check_ap(self, member: SyrupMember):
        last_rank = Ranks.lurker
        for rank in rank_list:
            last_idx = 0
            for i in rank.value['ap']:
                if member.ap <= i:
                    if last_idx == 0:
                        rank = last_rank
                        last_idx = last_rank.value['divisions']
                    if member.rank is not rank or member.division != rank.value['divisions'] + 1 - last_idx:
                        member.rank = rank
                        member.division = rank.value['divisions'] + 1 - last_idx
                        self.save_member(member)
                        await self.update_user_rank(rank, rank.value['divisions'] - last_idx, member.user_id)
                        return [rank.value['ap'][rank.value['divisions'] - last_idx], member.ap, i]
                    self.save_member(member)
                    return [rank.value['ap'][rank.value['divisions'] - last_idx], member.ap, i]
                last_idx += 1
            last_rank = rank

    def load_members(self):
        member_files = [file for file in listdir('./data/members/') if isfile(join('./data/members/', file))]
        for file in member_files:
            with open('./data/members/' + file, 'r') as j:
                json_data = json.load(j)
                new_member = self.SyrupMember(json_data)
                members[new_member.user_id] = new_member

    def save_members(self, mems: dict):
        for m in mems.values():
            self.save_member(m)

    def save_member(self, member: SyrupMember):
        member_dict = member.to_dict()
        with open('./data/members/' + str(member_dict['user_id']) + '.json', 'w') as file:
            json.dump(member_dict, file)

    def get_member_by_id(self, user_id: int):
        if user_id in members:
            member = members[user_id]
        else:
            return self.SyrupMember(user_id)
        return member

    async def format_user_name(self, user_id: int, division: int, master: bool = False, phoenix: bool = False,
                               reason: str = None):
        if master:
            division_string = Divisions.master.value
        elif phoenix:
            division_string = Divisions.phoenix.value
        else:
            division_string = get_division_by_number(division).value
        member = members[user_id]
        if member.nick is None:
            nick = division_string + self.bot.get_user(user_id).name
        else:
            nick = division_string + member.nick

        if user_id == config.NEKOMATA_ID:
            if not self.bot.get_guild(config.SYRUPSOCIETY_ID).get_member(config.NEKOMATA_ID).nick.startswith(
                    division_string):
                await self.bot.get_channel(config.BOT_SYSTEM_CHANNEL_ID).send('Nekomata, rank up to Division ' +
                                                                              str(
                                                                                  division + 1) + ' (' + division_string + ')')
            return
        if reason is None:
            await self.bot.get_guild(config.SYRUPSOCIETY_ID).get_member(user_id).edit(nick=nick)
        else:
            await self.bot.get_guild(config.SYRUPSOCIETY_ID).get_member(user_id).edit(nick=nick, reason=reason)

    def get_rank_roles(self):
        if self.rank_roles is None:
            self.rank_roles = [
                discord.utils.get(self.bot.get_guild(config.SYRUPSOCIETY_ID).roles, id=int(r.value['role_id']))
                for r in rank_list]
        return self.rank_roles

    async def update_user_rank(self, rank: Ranks, division: int, user_id: int):
        member = self.bot.get_guild(config.SYRUPSOCIETY_ID).get_member(user_id)
        if member is None:
            await self.bot.get_channel(config.BOT_SYSTEM_CHANNEL_ID).send('Could not get user: ' + str(user_id))
            return
        new_role = self.bot.get_guild(config.SYRUPSOCIETY_ID).get_role(int(rank.value['role_id']))
        if new_role not in member.roles:
            for role in self.get_rank_roles():
                await member.remove_roles(role, reason='Role update')
            await member.add_roles(new_role, reason='Role update')
        await self.format_user_name(user_id, division, rank is Ranks.master, rank is Ranks.syrup_phoenix,
                                    reason='Role update')
