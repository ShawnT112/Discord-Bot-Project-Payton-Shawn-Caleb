import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
import os
import asyncio
import logging
from mcstatus import JavaServer

load_dotenv()
# Bot configuration\
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = "!"
SERVER_IP = '147.185.221.31:36571'
SERVER_PORT = 'list-required.gl.joinmc.link'


### Bot Setup

intends = discord.Intents.default()
bot = commands.Bot(command_prefix=PREFIX, intents=intends)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
## BASIC COMMANDS

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


## SERVER COMMANDS

@bot.command()
async def status(ctx):
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
        status = server.status()
        await ctx.send(f"Server is online with {status.players.online} players!")
    except Exception:
        await ctx.send("Server is offline.")

# === READY EVENT ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# === RUN ===
if __name__ == "__main__":
    bot.run(TOKEN, log_handler=handler)
    