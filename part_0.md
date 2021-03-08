# 0 Getting your bot key
This is the first step in making a bot, the core identity and the first hurdle. 

## 0.1 Discord Account

If you don't have [this](https://discord.com/) already then this workshop might be confusing.

## 0.2 Developer Account

Ensure you have 2FA set up on your account and head over [here](https://discord.com/developers/applications) ready for [**0.3**](0.3).

## 0.3 Your First App

* Click the lovely CTA **New Application** button in the top right.
* Name it and hit the CTA **Create** button. 

## 0.4 Adding a Bot

* Head to the bot tab and hit the CTA **Add Bot** button.
* *For now you may want to untick the public bot option until your bot is 'ready' for general consumption.*
* Copy your client_id from the general information page of the app.
* Invite it to your test server by modifying this link:
    `https://discord.com/api/oauth2/authorize?client_id=[CLIENT_ID]&scope=bot&permissions=11328`

## 0.5 Getting a Token

Returning to the bot page copy the token from Build-A-Bot and put it in a `bot.key` file in the directory in which you will be working on your bot.
