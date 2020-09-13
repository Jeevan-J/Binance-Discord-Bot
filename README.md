# Binance-Discord-Bot

This is a simple python project which connects your Binance account to your Discord channel. We use Discord Bot feature to connect to Binance using Binance APIs 
and send Position updates to your Discord channel.

### Python Packages used
1. Discord - 1.0.1
2. Python-Binance - 0.7.5

First you need to setup a Discord Bot and create Binance API keys.

Follow this tutorial to create a discord bot and add to channel: https://discordpy.readthedocs.io/en/latest/discord.html

You need to provide the following IDs and TOKENs as ENVIRONMENT_VARIABLES before running the bot.
1. DISCORD_TOKEN : Token provided by Discord Bot
2. DISCORD_CHANNEL_ID : Target Channel ID to which you want to send messages/updates. Bot must be a member of that channel
3. BINANCE_API_KEY : API key can be found on Binance Profile page
4. BINANCE_API_SECRET : The secret key will be displayed only once when you create the API. So make sure to save it when you create the API
