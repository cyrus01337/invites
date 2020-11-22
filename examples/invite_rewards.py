"""
PEP8-complient cog showcasing invites by incorporating it into a basic
rewards system - once an invite has reached a certain number of uses,
the creator of the invite will be rewarded
"""
# cog.py
import discord
from discord.ext import commands


class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.thresholds = (10, 25, 50, 100)

    @commands.Cog.listener()
    async def on_invite_update(self, member, invite):
        await self.bot.wait_for_invites()
        print(f"{member} joined {member.guild} with invite {invite}")
        can_send = member.guild.system_channel is not None

        if invite.uses in self.thresholds and can_send:
            try:
                await member.guild.system_channel.send(
                    f"**Congratulations** to {invite.inviter} for reaching the "
                    f"**{invite.uses}** invite threshold! They will be "
                    f"rewarded with **{1000*invite.uses:,}** shiny rocky-wocks!"
                )
            except discord.Forbidden:
                print(f"[FAILED] {invite.code} @ {invite.uses} by "
                      f"{invite.inviter}")


def setup(bot):
    bot.add_cog(Invites(bot))


# bot.py
