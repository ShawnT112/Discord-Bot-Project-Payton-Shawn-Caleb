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
GUILD_ID = 1412905826783465605
ROLE_ID = 1421569616441905255

### Bot Setup
intents = discord.Intents.default()
intents.members = True  
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# BASIC COMMANDS
@tree.command(name="ping", description="Check if the bot is alive", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    if interaction.user.id == 395758958876295198:
        await interaction.response.send_message("Cheese Pizza!")
    else:
        await interaction.response.send_message("Pong!")



# SERVER STATUS
@tree.command(name="status", description="Check the Minecraft server status", guild=discord.Object(id=GUILD_ID))
async def status(interaction: discord.Interaction):
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
        status = server.status()
       
        if status.players.sample:
            player_list = ", ".join([player.name for player in status.players.sample])
            await interaction.response.send_message(
                f"Server is online with {status.players.online} players!\n"
                f"Online: {player_list}"
            )
        else:
            await interaction.response.send_message(
                f"Server is online with {status.players.online} players!\n"
                f"No player names available."
            )
    except Exception:
        await interaction.response.send_message("Server is offline.")



@tree.command(name="serverinfo", description="Show the Minecraft server's IP and port", guild=discord.Object(id=GUILD_ID))
async def serverinfo(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Server IP: `{SERVER_IP}`\nPort: `{SERVER_PORT}`"
    )


@tree.command(name="shutdown", description="Shut down the bot (owner only)", guild=discord.Object(id=GUILD_ID))
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id == 1198535129975488642:  
        await interaction.response.send_message("Shutting down...")
        await bot.close()
        import sys
        sys.exit(0)  # make sure the Python process fully stops
    else:
        await interaction.response.send_message("You don’t have permission.")




@tree.command(name="jointeam", description="Join a team by number (1-10)", guild=discord.Object(id=GUILD_ID))
async def jointeam(interaction: discord.Interaction, team_number: int):
    if team_number < 1 or team_number > 10:
        await interaction.response.send_message("Please pick a team number between 1 and 10.", ephemeral=True)
        return

    role_name = f"Team {team_number}"
    role = discord.utils.get(interaction.guild.roles, name=role_name)

    if role:
        # remove any other team roles first (optional)
        for r in interaction.user.roles:
            if r.name.startswith("Team "):
                await interaction.user.remove_roles(r)

        # add the new role
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"You joined **{role_name}**!")
    else:
        await interaction.response.send_message(f"Role `{role_name}` not found. Ask an admin to create it.", ephemeral=True)




#ROLE JOIN
@bot.event
async def on_member_join(member: discord.Member):
    role = member.guild.get_role(ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
            print(f"Assigned role to {member.name}")
        except Exception as e:
            print(f"Failed to assign role to {member.name}: {e}")
    else:
        print(f"Role with ID {ROLE_ID} not found.")

# READY EVENT
@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    # clear global commands (so no duplicates show up)
    await tree.sync()

    # register guild-only commands instantly
    await tree.sync(guild=guild)

    print(f"✅Logged in as {bot.user}")
    print(f"✅Slash commands synced to guild {GUILD_ID}")




# RUN
if __name__ == "__main__":
    bot.run(TOKEN, log_handler=handler)
