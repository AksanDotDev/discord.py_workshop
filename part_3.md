# 3 Extras

So this isn't expected to fit in the time for the workshop but it a more technical look at what we can be doing with our bot to help you move past this workshop. 
A noted absence in the workshop and still here is databases but for a persistent bot learning to using something like sqlalchemy and beginning to keep persistent state there, but for now lets do more things with discord.py.

## 3.1 Waiting in asyncio

Being able to wait as needed it really useful so here we are going to begin by changing the `knock_knock` function to wait after the final message and post a further reply.
As we talked about earlier asynio loops work hard to try and ensure that the program can be doing something, and simply waiting on the main thread would be bad so we can't just make a call to `sleep` here. 
But it is still pretty damn simple. 
Quick import of the relevant function.

```Python
from asyncio import sleep
```

And off we go, adding this section to our `knock_knock` function.

```Python
        with ctx.typing():
            await sleep(5.0)
            await ctx.send("lmao")
```
This is a non-blocking wait, which is what you'll typically want, allowing other commands to be executed while we are delaying this one, ideal. 
Additionally we use the `with` syntax alongside the `typing` function which allows our bot to appear as though they are typing in a channel while we wait. 
It's unneeded here but can be used if you're going to take a while to prepare a response or just want a bot to seem more human by using `typing` and delays. 

## 3.2 Status

Here we're going to look at adding post invoke hooks and updating the bot status.
As a fun thing to do with the status, bear with me, we're going to track how many jokes have been told with the help of this bot and display that. 

### 3.2.1 Keeping count

This means we're going to want to track everytime we have told a joke, hence the post invoke hook.
First things, first lets write our tracking code, adding a line to our `__init__` function.

```Python
        self.told = 0
```

Then set up our function to increment it we can do this after our commands and it's a very simple  

```Python
    async def increment_told(self, ctx):
        self.told += 1
```

Now we attach this to our two joke telling functions using their own `after_invoke` decorators so we get this.

```Python
    @lightbulb.after_invoke
    @knock_knock.after_invoke
    async def increment_told(self, ctx):
        self.told += 1
```

Now our number of jokes told is being updated, but we want to use it for something.

### 3.2.2 Updating our status

For this we're going to import a new part of the library that we haven't needed yet, the `tasks` helper.

```Python 
import discord.ext.tasks as det
```

Using this we can implement a loop that runs regularly and updates our status.
First we need to set up the decorators to make this command loop and the a little helper that makes the loop wait for the bot to be ready before starting.
```Python
    @det.loop(minutes=1)
    async def status_update(self):
        pass

    @status_update.before_loop
    async def before_status(self):
        await self.bot.wait_until_ready()
```

Now, much like facebook wishes we would we will be updating our status every minute, but before we start the loop we will wait for the bot to come online. 
In order to get what we want here we will want to import another class from the base of the library to make our status so we'll update this import.
```Python
from discord import TextChannel, GroupChannel, Member, Game
```
Finally it's time to actually update our status now so we'll replace that pass with this little bit of code. 
```Python
        await self.bot.change_presence(
            activity=Game(f"Jokes told: {self.told}")
        )
```
This will make a dummy game whith the string we pass and set that to our bot's status. 
But none of this will do anything if we don't set it off, we need to add this line to our `__init__` function to set is going.
```Python      
            self.status_update.start()
```
As a final touch we should put together this helper to the Cog, to run when the Cog is shut down and stop the loop. 
```Python
    def cog_unload(self):
        self.status_update.cancel()
```
Note that like `__init__` this clean up function is a blocking one, not an sync one. 

## 3.3 Some peace and quiet

Sometimes we will want our bot to take a break, or otherwise not run some commands for a while. 
We'll introduce here a bot wide hush function, but the concepts can be scaled from to the cog level down to specific functions using the same priciples. 

### 3.3.1 A shush function

So, lets start by adding a flag to our Cog in the `__init__` function.
```Python
        self.hushed = False
```

And lets add a function that will set that to true, wait and return it to being false. 
```Python
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
```

So here is a nice command with all the fluff we expect, an optional argument for the number of minutes to mute the Cog for and for bonus points we will add a reaction that we remove when the mute is over. 

Now we just need to make it so that all the commands are muted now too. 

### 3.3.2 A bot wide check

So, this is going to be a bit of explanation for very little code, in fact, just two lines. 

```Python
    def bot_check(self, ctx):
        return not self.hushed
```

This function has to be set within the Cog, and overrides a special function in the Cog class. 
By overriding this special function we can like here add a global check for the bot, but also have options on one time only checks, cog level checks and more. 

## 3.4 Catching some errors

As our last note on this little tour we're going to try some error catching, and with this revisit our best function yet `knock_knock`. 

### 3.4.1 Everything needs a handler

So, lets briefly attach an error handler that will catch a check failure, and base on what our only check is, reaction with the mute emoji we are making use of.
Here the interesting detail is using the decorator from the function we want to attach the error handler to in order to assign it.
Other error handlers can be done by listening for the `on_command_error` event globally or overriding the `cog_command_error` special function.
```Python
    @knock_knock.error
    async def error_handler_knock_knock(self, ctx, error):
        if isinstance(error, dec.errors.CheckFailure):
            await ctx.message.add_reaction("🔇")
```
Note if you're not to used to Python that we used `isinstance` to check the type of the error so we could be sure this was the error we were expecting, blindly catching all errors is very bad practise.

### 3.4.2 When to error

Now we've got a handler we can think about erroring out more eagerly within the command itself, lets do this by adding a timeout of a minute to each of the points where we await a response from the user like so.

```Python
        msg = await self.bot.wait_for('message', check=check, timeout=60)
```

This means we won't get clogged up waiting for a response forever, good for a bot that could be busy in many places, it will also throw an `asynio.TimeOutError` that we can check for and catch, but this won't make it to our error handler as it's not being throw by the command.
First however as that's not a discord error we need to import it for the type checking.

```Python
from asyncio import sleep, TimeoutError
```

Now we can look at trying the `wait_for` and raising an appropriate error to our error handler if it times out.

```Python
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
        except TimeoutError:
            raise dec.errors.UserInputError("User failed to input")
``` 

Now we have this we can check for it.

```Python
        if isinstance(error, dec.errors.UserInputError):
            await ctx.send("Well, if you aren't talking, I'm not listening.")
```

This relies on the way that errors are escalated in Python, and you could have handled it in the `knock_knock` function itself by putting each `wait_for` call in a `try` statement but as this can catch errors from both, and we want the same action this is arguably tidier. 
Something to investigate to streamline this further could be using [PEP622](https://www.python.org/dev/peps/pep-0622/) to do you matching rather than if statements. 
