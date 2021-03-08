# 1 First Steps

Lets get this bot up and working and prove that we have the basics of a bot.

## 1.1 Getting the bot online

This first step is connecting the bot to discord.

### 1.1.1 Imports

If you haven't already, install discord.py using `pip install discord.py`.

Next we will need to set up our core file, I called mine `core.py` and set up the imports, the first three are optional but recommended, feel free to ask me after the workshop about them, the fourth will bring in the core toolkit we will use. 

```Python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import discord.ext.commands as dec
```

### 1.1.2 Making the Bot Object

Rather than using a default client and shaping it into a bot we will be starting with a prebuilt bot object that gives us a lot of functionality for free. 
Lets set up a case insensitive bot and set the command prefix to when it's mentioned, this'll stop the bots on the test server from shouting over each other. 
*If you have your own server to test on feel free to use another prefix.*

```Python
WorkshopBot = dec.Bot(
    command_prefix=dec.when_mentioned,
    case_insensitive=True
)
```

### 1.1.3 Running the Bot

Now we're goign to use a common Python pattern to ensure that the bot is only ever initialised once in the main thread. 
This checks if the code is being invoked or somehow imported and only executes when we invoke the code, we then simply load the key from the file and then run the bot with this and reconnect set to true. 

```Python
if __name__ == "__main__":
    with open("bot.key") as key:
        token = key.read()

    WorkshopBot.run(token, reconnect=True)
```

## 1.2 Doing Something

Now our bot is online we should really make it do something more than just sitting there... watching.
Notable all the additions we make here will be done before the bot is run, setting all the commands in place before we press go.

### 1.2.1 Online Info

So, lets have it confirm that it's online by telling up who it's online as, simple right?
It is really, we just need to register an event listener with the bot. 
```Python
@WorkshopBot.listen("on_ready")
async def online_msg():
    print(f"Online as {WorkshopBot.user}")
```
So to break this down a bit more, it's a function that prints the user to the commandline, called `on_ready()`.
This name is key as it means we register it, via the `@Workshop.event` decorator for the `on_ready` event. 

One of the big notes here is the `async` keyword before `def`. 

#### 1.2.2 Async Loops

So, bit of an aside but one of the key concepts of a discord.py bot is a asynchronous execution loop that allows multiple things to be occuring in parallel. 
Async functions are coroutines that perform asyncio as Python calls it, asynchronous input output.
Due to the nature of various commands being executed between the bot's host and the remote discord servers a good bot implimentation will keep doing other things while waiting for replies to the messages it sends to the discord servers.
To do this your bot will operate in a loop of checking for events and for asyncio operations to finish, an `async` function, as any called in this loop must be, will be able to hand control away so other things can be done in the loop while it, typically, waits for a response from the discord server. 
We will explore this a bit more later when we encounter the `await` keyword, but for now just recognise all the functions working in the bot will need to be `async def`. 

### 1.2.3 Mic Test

Lets have a look at making our bot actually talk to us, just a little. 
If we following what we've done we'd make this:
```Python
@WorkshopBot.listen("on_message")
async def test_response(message):
    if message.content.lower() == "test":
        await message.channel.send("Testing, testing, 1, 2, 1, 2!")
```
But this is bad for reasons:
* It's just bad
* It blocks other commands
* It doesn't work with or respect our prefix
* It makes us tinker with everything manually
* It lacks a lot of goodness we will encounter later

So how we work *with* the library and set up a command.
```Python
@WorkshopBot.command(
    name="Test"
)
async def test_response(ctx):
    await ctx.send("Testing, testing, 1, 2, 1, 2!")
```
So, this may not be immediately nicer, it's an extra line, but we could compress it more if we wanted but look at what we have:
* It's better
* Works alside other commands
* Respects our prefix
* Gives us the option to set some command variables (we'll use this later)
* Gives us some inherent goodness

Something to note here is we need to `await` the call 
The `ctx` object is a fantastically powerful one, it operates as needed as the message that triggered this and the channel that it was sent in and gives us one stop for all the information that we need.

### 1.2.4 Finishing touches

So, we've got the very bare bones of a bot here, hopefully you can see how you start building one up, but we're not done, even on our basic example.

#### 1.2.4.1 A command by any other name
Lets add some alternate names in case we want to use them.
```Python
    aliases=["ping", "check"]
```
By setting aliases we can allow a command to respond to multiple different invocations, if needs be we can always get the name that was used back by using `ctx.invoked_with`, see, powerful object.
There is more that you can do to insure that your commands are set up all within arguments to the command decorator. 

#### 1.2.4.2 Everybody's favourite thing

Now, lets be good programmers and add one last thing. 
```Python
@WorkshopBot.command(
    name="Test",
    aliases=["ping", "check"]
)
async def test_response(ctx):
    """Simple call and response to test if we are online"""
    await ctx.send("Testing, testing, 1, 2, 1, 2!")
```
You see it? 
Well, go to your bot and invoke the `help` command and you'll see it there too. 
Anything that we add to a command as a docstring will be automatically attached as a description in the compiled `help` command.
This is one of the things we got for free by using a `Bot` rather than a plain client and we'll see more about the extend of it later.