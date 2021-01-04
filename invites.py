"""
MIT License

Copyright (c) 2020-2021 cyrus01337, XuaTheGrate

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
from typing import Dict, Optional
import time

import discord
from discord.ext import commands, tasks


class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._invites_ready = asyncio.Event()

        self.bot.invites = {}
        self.bot.get_invite = self.get_invite
        self.bot.wait_for_invites = self.wait_for_invites

        self.bot.loop.create_task(self.__ainit__())

    async def __ainit__(self):
        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:
            self.bot.invites[guild.id] = await self.fetch_invites(guild) or {}

        self.update_invite_expiry.start()

    @tasks.loop()
    async def delete_expired(self):
        invites = self.bot.expiring_invites
        expiry_time = min(invites.keys())
        inv = invites[expiry_time]
        await asyncio.sleep(expiry_time - (time.time() - self.bot.last_update))
        self.delete_invite(inv)
        self.bot.expiring_invites.pop(expiry_time, None)

    @delete_expired.before_loop
    async def wait_for_list(self):
        await self.wait_for_invites()

    @tasks.loop(minutes=29)
    async def update_invite_expiry(self):
        flattened = [invite for inner in self.bot.invites.values() for invite in inner.values()]
        current = time.time()
        self.bot.expiring_invites = {inv.max_age - current + inv.created_at.timestamp(): inv for inv in flattened if inv.max_age != 0}
        self.bot.last_update = current
        if self.update_invite_expiry.current_loop == 0:
            self._invites_ready.set()


    def delete_invite(self, invite: discord.Invite):
        entry_found = self.get_invites(invite.guild.id)
        entry_found.pop(invite.code, None)

    def get_invite(self, code: str) -> Optional[discord.Invite]:
        for invites in self.bot.invites.values():
            find = invites.get(code)

            if find:
                return find
        return None

    def get_invites(self, guild_id: int) -> Optional[Dict[int, str]]:
        return self.bot.invites.get(guild_id, None)

    async def wait_for_invites(self):
        if not self._invites_ready.is_set():
            await self._invites_ready.wait()

    async def fetch_invites(self, guild) -> Optional[Dict[int, discord.Invite]]:
        try:
            invites = await guild.invites()
        except discord.HTTPException:
            return None
        else:
            return {invite.code: invite for invite in invites}

    async def _schedule_deletion(self, guild: discord.Guild):
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
        cached = self.bot.invites.get(invite.guild.id, None)

        if cached:
            cached[invite.code] = invite

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        self.delete_invite(invite)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        invites = self.bot.invites.get(channel.guild.id)

        if invites:
            for invite in invites.values():
                # changed to use id because of doc warning
                if invite.channel.id == channel.id:
                    invites.pop(invite.code)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        invites = await self.fetch_invites(guild) or {}
        self.bot.invites[guild.id] = invites

    @commands.Cog.listener()
    async def on_guild_available(self, guild):
        # reload all invites if they have changed in the time
        # that the guilds were unavailable
        self.bot.invites[guild.id] = self.fetch_invites(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.create_task(self._schedule_deletion(guild))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        invites = await self.fetch_invites(member.guild)

        if invites:
            # we sort the invites to ensure we are comparing
            # A.uses == A.uses
            invites = sorted(invites.values(), key=lambda i: i.code)
            cached = sorted(self.bot.invites[member.guild.id].values(),
                            key=lambda i: i.code)

            # zipping is the easiest way to compare each in order, and
            # they should be the same size? if we do it properly
            for old, new in zip(cached, invites):
                if old.uses < new.uses:
                    self.bot.invites[member.guild.id][old.code] = new
                    self.bot.dispatch("invite_update", member, new)
                    break

    @commands.command()
    async def invitestats(self, ctx):
        # PEP8 + same code, more readability
        cache = {}

        for guild, invites in self.bot.invites.items():
            cached_invites = cache[guild] = {}

            for invite in invites.values():
                cached_invites[invite.code] = invite.uses
        await ctx.send(json.dumps(cache))


def setup(bot):
    bot.add_cog(Invites(bot))
