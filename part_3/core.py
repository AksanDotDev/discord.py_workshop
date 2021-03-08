from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import discord.ext.commands as dec
from jokes_cog import Jokes

WorkshopBot = dec.Bot(
    command_prefix=dec.when_mentioned,
    case_insensitive=True
)


@WorkshopBot.listen("on_ready")
async def online_msg():
    print(f"Online as {WorkshopBot.user}")
    for name in WorkshopBot.cogs.keys():
        print(f" Loaded: {name}")


@WorkshopBot.command(
    name="test",
    aliases=["ping", "check"]
)
async def test_response(ctx):
    """Simple call and response to test if we are online"""
    await ctx.send("Testing, testing, 1, 2, 1, 2!")


if __name__ == "__main__":
    with open("bot.key") as key:
        token = key.read()

    WorkshopBot.add_cog(Jokes(WorkshopBot))

    WorkshopBot.run(token, reconnect=True)
