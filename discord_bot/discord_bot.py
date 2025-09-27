import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os
import logging
from mcstatus import JavaServer

load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_IP = '147.185.221.31'
SERVER_PORT = 36571

### Bot Setup
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

## BASIC COMMANDS
@tree.command(name="ping", description="Check if the bot is alive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

## SERVER COMMANDS
@tree.command(name="status", description="Check the Minecraft server status")
async def status(interaction: discord.Interaction):
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
        status = server.status()
        await interaction.response.send_message(
            f"✅ Server is online with {status.players.online} players!"
        )
    except Exception:
        await interaction.response.send_message("Server is offline.")

# === READY EVENT ===
@bot.event
async def on_ready():
    # Sync commands with Discord
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")
    print("✅ Slash commands synced")

# === RUN ===
if __name__ == "__main__":
    bot.run(TOKEN, log_handler=handler)
