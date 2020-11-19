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
import asyncio
import json
from typing import Optional

import discord
from discord.ext import commands


class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.invites = {}
        self.bot.get_invite = self.get_invite

        self.bot.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:
            self.bot.invites[guild.id] = await self.fetch_invites(guild) or {}

    def get_invite(self, code: str):
        for invites in self.bot.invites.values():
            find = invites.get(code)

            if find:
                return find
        return None

    def get_invites(self, guild_id: int) -> Optional[dict[int, str]]:
        return self.bot.invites.get(guild_id, None)

    async def fetch_invites(self, guild):
        try:
            invites = await guild.invites()
        except discord.HTTPException:
            return None
        else:
            return {invite.code: invite for invite in invites}

    async def schedule_deletion(self, guild):
        seconds_passed = 0

        while seconds_passed < 300:
            seconds_passed += 1

            if guild in self.bot.guilds:
                return
            await asyncio.sleep(1)

        if guild not in self.bot.guilds:
            self.bot.invites.pop(guild.id, None)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        print(f"created invite {invite} in {invite.guild}")
        cached = self.bot.invites[invite.guild.id]

        if cached:
            cached[invite.code] = invite

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        entry_found = self.get_invites(invite.guild.id)
        entry_found.pop(invite.code, None)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        purging = []
        invites = self.bot.invites[channel.guild.id]

        for invite in invites.values():
            if invite.channel == channel:
                purging.append(invite.code)

        for code in purging:
            invites.pop(code, None)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        invites = await self.fetch_invites(guild) or {}
        self.bot.invites[guild.id] = invites

    async def on_guild_available(self, guild):
        invites = await guild.invites()
        cached = self.bot.invites[guild.id]

        for invite in invites:
            # reload all invites if they have changed in the time that
            # the guilds were unavailable
            find = cached.get(invite.code)

            if find and invite != find:
                cached[invite.code] = invite

    async def on_guild_remove(self, guild):
        self.bot.create_task(self.schedule_deletion(guild))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        invites = await self.fetch_invites(member.guild)
        if invites is not None:

            # we sort the invites to ensure we are comparing A.uses == A.uses
            invites = sorted(invites.values(), key=lambda i: i.code)
            cached = sorted(self.bot.invites[member.guild.id].values(), key=lambda i: i.code)

            # zipping is the easiest way to compare each in order, and they should be the same size? if we do it properly
            for old, new in zip(cached, invites):
                if old.uses != new.uses:
                    self.bot.invites[member.guild.id][old.code] = new
                    self.bot.dispatch("invite_update", member, new)
                    break

    @commands.command()
    async def invite_stats(self, ctx):
        # PEP8 + same code, more readability
        cache = {}

        for guild, invites in self.bot.invites.items():
            cached_invites = cache[guild] = {}

            for invite in invites.values():
                cached_invites[invite.code] = invite.uses
        await ctx.send(json.dumps(cache))


def setup(bot):
    bot.add_cog(Invites(bot))
