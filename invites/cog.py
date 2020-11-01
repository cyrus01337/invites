"""
MIT License

Copyright (c) 2020 cyrus01337, XuaTheGrate

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import discord
from discord.ext import commands


class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.cache = {}

        self.bot.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:
            invites = await guild.invites()

            if invites:
                self.cache[guild.id] = invites

    # would this ever be used by end-users?
    def get_invite(self, code: str):
        for invites in self.cache.values():
            invite_found = discord.utils.get(invites, code=code)

            if invite_found:
                return invite_found
        return None

    def get_invites(self, guild_id: int):
        return self.cache.get(guild_id, None)

    async def on_invite_create(self, invite):
        # (maybe) send event here
        cached = self.get_invites(invite.guild.id)

        if cached:
            cached.append(invite)

    async def on_invite_delete(self, invite):
        # (maybe) send event here
        entry_found = self.get_invites(invite.guild.id)

        if entry_found:
            invite_found = discord.utils.get(entry_found, code=invite.code)

            if invite_found:
                try:
                    entry_found.remove(invite_found)
                except ValueError:
                    # retained for debugging purposes? maybe add to
                    # Discord.py logging? unsure how to achieve this...
                    print("ValueError (on_invite_delete)")

    # TODO: to verify redundancy - check if invites are available for
    # deleted channels
    async def on_guild_channel_delete(self, channel):
        pass

    async def on_guild_join(self, guild):
        # (maybe) send event here
        pass

    # can be used if not run during guild cache population
    # spoiler: it's not
    # async def on_guild_available(self, guild):
    #     pass

    # considering - remove cache entry after set time passes in tasks
    # async def on_guild_remove(self, guild):
    #     pass

    async def on_member_join(self, member):
        # send event here
        pass


def setup(bot):
    bot.add_cog(Invites(bot))
