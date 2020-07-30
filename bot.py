# bot.py
import os, json
import discord
from discord.ext import commands, tasks
import logging
from binance.client import Client

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

TOKEN = os.getenv('DISCORD_TOKEN')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
CHANNEL_ID = os.getenv('CHANNEL_ID')

binanceClient = Client(BINANCE_API_KEY,BINANCE_API_SECRET)

with open('FAV_LIST.json') as f:
    data = json.load(f)

FUTURES_FAV_LIST = data['FUTURES']
SPOT_FAV_LIST = data['SPOT']

def get_future_position(symbol):
    position = None
    positions = list(filter(lambda f:(f['symbol']==symbol),binanceClient.futures_account()['positions']))
    if positions:
        position = positions[0]
    return position

bot = commands.Bot(command_prefix='>')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def add_fav(ctx, account, symbol):
    FUT_SYMBOLS = [sym['symbol'] for sym in binanceClient.futures_exchange_info()['symbols']]
    SPOT_SYMBOLS = [sym['symbol'] for sym in binanceClient.get_all_tickers()]
    if account.upper() == "FUT":
        if symbol in FUT_SYMBOLS:
            FUTURES_FAV_LIST.append(symbol)
        else:
            await ctx.send("Provided SYMBOL or CRYPTO is not available in Futures")
    elif account.upper() == "SPOT":
        if symbol in SPOT_SYMBOLS:
            SPOT_SYMBOLS.append(symbol)
        else:
            await ctx.send("Provided SYMBOL or CRYPTO is not available in SPOT")
    else:
        await ctx.send('Provided Account Type is not valid. Please use FUT for Futures and SPOT for spot')

@bot.command()
async def favs(ctx):
    message = "FUTURES FAVOURITE LIST\n"
    for i, symbol in enumerate(FUTURES_FAV_LIST):
        message += str(i+1) + ". " + symbol + "--> Last Price: "+ binanceClient.get_ticker(symbol=symbol)['lastPrice']+"\n"
    message += "\n\nSPOT FAVOURITE LIST"
    for i, symbol in enumerate(SPOT_FAV_LIST):
        message += str(i+1) + ". " + symbol + "--> Last Price: "+ binanceClient.get_ticker(symbol=symbol)['lastPrice']+ "\n"
    await ctx.send(message)
    
@bot.command()
async def fubln(ctx):
    balance_list = binanceClient.futures_account_balance()
    message = "-"*35 + "\n"
    message += "-"*3 + "ACCOUNT BALANCE" + "-"*3 + "\n"
    message += "-"*35 +"\n"
    for balance in balance_list:
        message += balance['asset']+" : "+balance['balance']+"\n"
    message += "-"*35
    await ctx.send(message)

@tasks.loop(seconds=60)
async def favs_info():
    message = "INFO of Favourite Crytos\n\n"
    message += "FUTURES\n"
    for i, symbol in enumerate(FUTURES_FAV_LIST):
        position = get_future_position(symbol)
        message += str(i)+". "+position['symbol']+" --> unrealizedProfit : "+position['unrealizedProfit']
    message_channel = await bot.fetch_channel(CHANNEL_ID)
    print(f"Got channel {message_channel} for {CHANNEL_ID}")
    await message_channel.send(message)

@favs_info.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished waiting")

favs_info.start()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

bot.run(TOKEN)