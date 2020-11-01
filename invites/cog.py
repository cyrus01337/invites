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
            self.cache[guild.id] = await self.fetch_invites(guild) or {}

    # would this ever be used by end-users?
    def get_invite(self, code: str):
        for invites in self.cache.values():
            find = invites.get(code)
            if find:
                return find
        return None

    def get_invites(self, guild_id: int):
        return self.cache.get(guild_id, None)

    @commands.command()
    async def invite_stats(self, ctx):
        import json
        cache = {g: {i.code: i.uses for i in invs.values()} for g, invs in self.cache.items()}
        await ctx.send(json.dumps(cache))

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        # (maybe) send event here
        print("created invite {invite} in {invite.guild}")
        cached = self.cache[invite.guild.id]

        if cached:
            cached[invite.code] = invite

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        # (maybe) send event here
        entry_found = self.get_invites(invite.guild.id)

        if entry_found:
            entry_found.pop(invite.code, None)

    # TODO: to verify redundancy - check if invites are available for
    # deleted channels
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        pass

    async def fetch_invites(self, guild):
        try:
            invites = await guild.invites()
        except discord.HTTPException:
            return None
        else:
            return {invite.code: invite for invite in invites}

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # (maybe) send event here
        invites = await self.fetch_invites(guild) or {}
        self.cache[guild.id] = invites

    # can be used if not run during guild cache population
    # spoiler: it's not
    # async def on_guild_available(self, guild):
    #     pass

    # considering - remove cache entry after set time passes in tasks
    # async def on_guild_remove(self, guild):
    #     pass

    @commands.Cog.listener()
    async def on_member_join_invite(self, member, invite):
        print(f"{member} joined {member.guild} with invite {invite}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        invites = await self.fetch_invites(member.guild)
        if invites is not None:

            # we sort the invites to ensure we are comparing A.uses == A.uses
            invites = sorted(invites.values(), key=lambda i: i.code)
            cached = sorted(self.cache[member.guild.id].values(), key=lambda i: i.code)

            # zipping is the easiest way to compare each in order, and they should be the same size? if we do it properly
            for old, new in zip(cached, invites):
                if old.uses != new.uses:
                    self.cache[member.guild.id][old.code] = new
                    self.bot.dispatch("member_join_invite", member, new)
                    break
