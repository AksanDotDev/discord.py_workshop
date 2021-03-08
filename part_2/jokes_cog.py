from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import discord.ext.commands as dec
from typing import Union
from discord import TextChannel, GroupChannel, Member


class Jokes(dec.Cog):
    """A simple cog to try and help tell some jokes"""

    def __init__(self, bot):
        self.bot = bot

    @dec.group(
        name="knock",
        case_insensitive=True,
        invoke_without_command=True,
        pass_context=True
    )
    async def knock_root(self, ctx):
        """The root of the "knock knock" routine"""
        await ctx.send("I can't hear you!")

    @knock_root.command(
        name="knock"
    )
    async def knock_knock(self, ctx):
        """The knock knock routine command"""
        await ctx.send("Who's there?")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        msg = await self.bot.wait_for('message', check=check)

        rps = msg.content.strip().rstrip(".").capitalize()
        await ctx.send(f"{rps}, who?")

        msg = await self.bot.wait_for('message', check=check)

        await msg.add_reaction('🤣')

    @dec.command(
        name="lightbulb",
        usage=["subjects", "target"]
    )
    async def lightbulb(
                self, ctx, sbj: str,
                tgt: Union[TextChannel, GroupChannel, Member] = None
            ):
        """A command to set up a lightbulb joke"""
        rps = f"How many {sbj} does it take to change a lightbulb?"
        if tgt:
            await tgt.send(rps)
        else:
            await ctx.send(rps)
