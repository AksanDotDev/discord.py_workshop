# 2 Machines are lots of cogs

If we want to build any non-trivial bot we will want some degree of modularity and structure, so we turn to the `Cog` system of the discord.py library for our structure. 

# 2.1 Making a Cog

So, now we make a new file where we are going to keep our new `Cog` that we will make, I've called mine `jokes_cog.py` but you can change it here and throughout if you want. 
Same imports as before.

```Python
class Jokes(dec.Cog):
    """A simple cog to try and help tell some jokes"""

    def __init__(self, bot):
        self.bot = bot
```
We're just going to set up a simple class here, it inherits from the existing `Cog` class and we do some basic set up so it has an idea of its surroundings when it runs.
We might be revisting this `__init__` function later so just keep in mind this is basically our constructor.
Docstrings are for winners!

## 2.2 Fitting it in

So, Lara has reached the top of the waterfall, the time has come to put the cog in place to make the machine work. 
First we need to get our new class over into our core which is as simple as importing it from the module that it's defined in into our original file.
*You could just import the module but this is a cleaner method that I prefer as it doesn't pollute the namespace with any helper functions that exist in that module.*

```Python
from jokes_cog import Jokes
```

Now we just initialize and add the cog to our bot, we could do this in a lot of places, but we're going to do this in the if-main block but **before** our call to `run`. 

```Python
    WorkshopBot.add_cog(Jokes(WorkshopBot))
```

And to ice things we'll add this little touch to our `on_ready` function to show that we've actually done something.

```Python
    for name in WorkshopBot.cogs.keys():
        print(f" Loaded: {name}")
```

Now we can turn the handle. 

## 2.3 Groups and commands

So, lets add something to our cog to make it worthwhile.

### 2.3.1 Groundwork

We're going to be making a bot to play the fool in 'knock knock' jokes, so bear with me as we're going to make stop offs at some individual focii along the way but it will come together.
This will start with making a group, this allows commands to have subcommands and is how we will get our 'knock knock' joke to work. 
If you want an example of how subcommands work, think of them like the way `git` handles its commands, you use commands like `git stage`, `git commit`, and `git push` if they were being handled by discord.py this would be a group called `git` with commands in it called `stage`, `commit`, and `push`. 

So that's some theory, lets get started in practise. 

```Python
    @dec.group(
        name="knock",
        case_insensitive=True,
        invoke_without_command=True,
        pass_context=True
    )
    async def knock_root(self, ctx):
        """The root of the "knock knock" routine"""
        await ctx.send("I can't hear you!")
```

At it's heart we just attach a decorator the same way we did with a command only this is for a group and comes from the library not the bot, this is because we're in a `Cog` now, and because that's a class we add a `self` argument to the function.
Otherwise this isn't much more complex than `test_response`, right?.

Okay, so about all those parameters... 
Case insensitivity must be set on a group by group basis, it won't follow the bot and here we carry on and set it to be true. 
Now `invoke_without_command` is a slightly deceptive name as when true this group command is only invoked if there are no subcommands, if it's false it would be invoked regardless. 
Might be easier to think of this as the negation of `invoke_with_command`.
Finally, `pass_context` tells this to pass the context on trasparently to the subcommands if they are invoked.

### 2.3.2 A subcommand

So, now we add our command to this group. 

```Python
    @knock_root.command(
        name="knock"
    )
    async def knock_knock(self, ctx):
        """The knock knock routine command"""
        await ctx.send("Who's there?")
```

Nothing ground breaking here but note our decorator begins with the name of our group function. 

Bit boring so far though.

## 2.4 Complex commands

Okay, so to play through a knock knock joke we're going to have to be a bit more clever than our previous commands.

### 2.4.1 Waiting for a response

Obviously what we really want to be able to do is capture the next thing that the invoker says, as that'll be the next part of the joke, so lets look at how to do that.
The best thing we can do is wait for a message to be sent that fits that brief using the `wait_for` coroutine of the bot, but first we will need to write a check so we know what we are looking for.

```Python
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
```

We define this quick check on messages within our `knock knock` function, using the `ctx` object to help us out on the details. 
Now we can go ahead and tell the bot to wait for a message matching these parameters and give it to our function.

```Python
        msg = await self.bot.wait_for('message', check=check)
```

Note we can assign using an awaited value, we just won't be continuing until we recieve it and we use the reference to the bot that we popped in our initialisation earlier to get this done.

### 2.4.2 Back and forth

So, now we have our second message from the user, we can reply.
First, lets do some tidying up of their input, which we find in the `content` property of the message so it fits with our response, stripping spaces, final fullstops and capitalizing it.

```Python
        rps = msg.content.strip().rstrip(".").capitalize()
```
So, now we just have to send this off like the fool we are. 

```Python
        await ctx.send(f"{rps}, who?")
```
And we're done? 
Maybe not quite, if we're being polite we can use the same code we just used to wait for the setup to wait for the punchline and laugh.

```Python
        msg = await self.bot.wait_for('message', check=check)
        
        await msg.add_reaction("🤣")
```
Adding these two lines at the end, and the joys of unicode being valid strings means we can show our mirth with a 'ROFL' react. 

## 2.5 Exchanges are good...

So, let's talk about arguments, we kinda used one in the middle of that back and forth in how we processed the user input but now lets take some explicitly. 

### 2.5.1 Taking an argument

Continuing our joke theme lets the bot set up some jokes for us to tell, this is going to be a command that helps us set up a light bulb joke and takes a string argument to do so.

```Python
    @dec.command(
        name="lightbulb",
        usage=["subjects"]
    )
    async def lightbulb(self, ctx, subject: str):
        """A command to set up a lightbulb joke"""
        await ctx.send(
            f"How many {subject} does it take to change a lightbulb?"
        )
```

So, let take this apart.
First we have a new helper, `usage`, this allows us to provide a string that replaces the arguments in the command examples found in `help`.
This can be useful for providing guidance on how to use your bot's more complex commands and we'll expand it later.
Second we have a new argument to our command that tells it to look for a `str` given after the argument. 
This works, but we can do better...

### 2.5.2 Debates, or sofisticated arguments

Right now this bot will respond in the context that it got the command, but this is a bit limiting.
Sometimes we want to have our joke set up in another channel, or to set it up in a DM (okay, this is stretching the premise a bit, but think if you want to tell your bot where to send a log file or such), lets make it possible to do that. 

First we need to import a little help though.

```Python
from typing import Union
from discord import TextChannel, GroupChannel, Member
```

Here we are bringing in some support for typing, you see discord.py has a lot of super intelligent converters that can give us arguments in the form we need them, but to do this we need to be able to tell the library what form that is. 
Here is where we make some heavier use of the typing library that with the `str` hint and we want to use `Union` to do it.
In effect `Union` lets us give a list of potential types for an argument to be, here either a channel or a person. 
*Side note, how you get a bot into a group DM is an advanced exercise left for the reader.*
Now we can tell it the kinds of argument we want and it will try to convert whatever is passed in that space into one of those types as best it can. 

```Python
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
```
Now we see how we implement this, giving a default value `None` makes the argument optional, we've added to the `usage` parameter and then we've done some logic.
Okay, logic is glossing over things.
In case you didn't know, Python has falsy and truthy values, with `None` being falsey and any object being truthy.
This lets us do the simple `if tgt:` that will be executed if we have a `tgt` argument that isn't `None`. 
Finally, the fact that all of those objects, channels and people, can be sent messages means we don't need to check the type we can just fire off the message. 

A final note on usage here, you can pass multiple words, including white space to a single argument, but you need to use quotes in your message e.g. `"text more text"`, in order to do it. 
