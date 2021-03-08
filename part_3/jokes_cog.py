from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import discord.ext.commands as dec
import discord.ext.tasks as det
from asyncio import sleep, TimeoutError
from typing import Union
from discord import TextChannel, GroupChannel, Member, Game


class Jokes(dec.Cog):
    """A simple cog to try and help tell some jokes"""

    def __init__(self, bot):
        self.bot = bot
        self.told = 0
        self.hushed = False
        self.status_update.start()

    def cog_unload(self):
        self.status_update.cancel()

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

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
        except TimeoutError:
            raise dec.errors.UserInputError("User failed to input")

        rps = msg.content.strip().rstrip(".").capitalize()
        await ctx.send(f"{rps}, who?")

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
        except TimeoutError:
            raise dec.errors.UserInputError("User failed to input")

        await msg.add_reaction('🤣')

        with ctx.typing():
            await sleep(5.0)
            await ctx.send("lmao")

    @knock_knock.error
    async def error_handler_knock_knock(self, ctx, error):
        if isinstance(error, dec.errors.CheckFailure):
            await ctx.message.add_reaction("🔇")
        if isinstance(error, dec.errors.UserInputError):
            await ctx.send("Well, if you aren't talking, I'm not listening.")

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

    @lightbulb.after_invoke
    @knock_knock.after_invoke
    async def increment_told(self, ctx):
        self.told += 1

    @det.loop(minutes=1)
    async def status_update(self):
        await self.bot.change_presence(
            activity=Game(f"Jokes told: {self.told}")
        )

    @status_update.before_loop
    async def before_status(self):
        await self.bot.wait_until_ready()

    @dec.command(
        name="hush",
        aliases=["quiet", "shush", "sh"],
        usage=["minutes"]
    )
    async def hush(self, ctx, mns: int = 5):
        """Mutes the Cog's interactions n minutes"""
        await ctx.message.add_reaction("🔇")
        self.hushed = True
        await sleep(mns*60)
        self.hushed = False
        await ctx.message.remove_reaction("🔇", self.bot.user)

    def bot_check(self, ctx):
        return not self.hushed
