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

FAV_LIST = {}
with open('FAV_LIST.json') as f:
    FAV_LIST = json.load(f)


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
            FAV_LIST['FUTURES'][symbol] = {}
        else:
            await ctx.send("Provided SYMBOL or CRYPTO is not available in Futures")
    elif account.upper() == "SPOT":
        if symbol in SPOT_SYMBOLS:
            FAV_LIST['SPOT'][symbol] = {}
        else:
            await ctx.send("Provided SYMBOL or CRYPTO is not available in SPOT")
    else:
        await ctx.send('Provided Account Type is not valid. Please use FUT for Futures and SPOT for spot')
    with open('FAV_LIST.json','w') as f:
        json.dump(FAV_LIST, f)

@bot.command()
async def favs(ctx):
    message = "FUTURES FAVOURITE LIST\n"
    for i, symbol in enumerate(FAV_LIST['FUTURES'].keys()):
        message += str(i+1) + ". " + symbol + "--> Last Price: "+ binanceClient.get_ticker(symbol=symbol)['lastPrice']+"\n"
    message += "\n\nSPOT FAVOURITE LIST"
    for i, symbol in enumerate(FAV_LIST['SPOT'].keys()):
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
async def futures_position_alerts():
    futures_info = binanceClient.futures_account()
    positions_info = binanceClient.futures_position_information()
    positions = futures_info['positions']
    message_channel = await bot.fetch_channel(CHANNEL_ID)
    print(f"Got channel {message_channel} for {CHANNEL_ID}")
    if float(futures_info['totalMaintMargin'])/float(futures_info['totalMarginBalance']) > 40.0:
        await message_channel.send("Your positions' Margin Ratio is greater than 40%. Please consider taking a look at it.")
    for position in positions:
        symbol = position['symbol']
        alert = False
        message = "------"+symbol+" POSITION ALERT!------\n"
        position_info = list(filter(lambda f:(f['symbol']==symbol),positions_info))[0]
        if float(position_info['positionAmt']) != 0.0:
            if float(position['unrealizedProfit']) < -1.0 :
                message += "Unrealized Profit is going down! LOSS : "+ str(position['unrealizedProfit']) +"\n"
                alert = True
            if (float(position_info['markPrice'])-float(position_info['liquidationPrice']))/(float(position_info['entryPrice'])-float(position_info['liquidationPrice'])) <= 0.4:
                message += "Mark price is moving closer to Liquidation Price. Your position may be liquidated soon.\n Mark Price:"+ str(position_info['markPrice']) +"\n Liquidation Price:"+str(position_info['liquidationPrice'])+"\n"
                alert = True
        if alert:
            await message_channel.send(message)

@futures_position_alerts.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished waiting")

futures_position_alerts.start()

#@tasks.loop(seconds=60)
#async def favs_info():
#    message = "INFO of Favourite Crytos\n\n"
#    message += "FUTURES\n"
#    for i, symbol in enumerate(FAV_LIST['FUTURES'].keys()):
#        position = get_future_position(symbol)
#        message += str(i)+". "+position['symbol']+" --> unrealizedProfit : "+position['unrealizedProfit']
#    message_channel = await bot.fetch_channel(CHANNEL_ID)
#    print(f"Got channel {message_channel} for {CHANNEL_ID}")
#    await message_channel.send(message)
#
#@favs_info.before_loop
#async def before():
#    await bot.wait_until_ready()
#    print("Finished waiting")
#
#favs_info.start()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

bot.run(TOKEN)