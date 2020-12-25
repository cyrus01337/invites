"""
PEP8-complient bot showcasing invites by incorporating it into a basic
rewards system - once an invite has reached a certain number of uses,
the creator of the invite will be rewarded
"""
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="prefix ")
bot.thresholds = (10, 25, 50, 100)


@bot.event
async def on_ready():
    print("Loaded", bot.user.name, end="\n\n")


@bot.listen()
async def on_invite_update(member, invite):
    await bot.wait_for_invites()
    print(f"{member} joined {member.guild} with invite {invite}")
    can_send = member.guild.system_channel is not None

    if invite.uses in bot.thresholds and can_send:
        try:
            # I am sorry that rocky-wocks was all that came to mind
            await member.guild.system_channel.send(
                f"**Congratulations** to {invite.inviter} for reaching the "
                f"**{invite.uses}** invite threshold! They will be "
                f"rewarded with **{1000*invite.uses:,}** shiny rocky-wocks!"
            )
        except discord.Forbidden:
            print(f"[FAILED] {invite.code} @ {invite.uses} by "
                  f"{invite.inviter}")


# ?tag token - :^)
bot.run("MjM4NDk0NzU2NTIxMzc3Nzky.CunGFQ.wUILz7z6HoJzVeq6pyHPmVgQgV4")
