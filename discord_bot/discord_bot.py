# discord_bot.py
import os
import logging
import random
import socket
from typing import Dict, List, Optional

import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv

try:
    from mcstatus import JavaServer
except Exception:
    JavaServer = None  # allow offline tests without mcstatus installed

# ---------------------- Config ----------------------
PREFIX = "/"
SERVER_IP = "147.185.221.31"   # <-- change if needed
SERVER_PORT = "36571"          # game TCP port (string for convenience)
QUERY_PORT: Optional[str] = "36571"  # None => reuse game port; or set to your query.port
QUERY_TIMEOUT_SEC = 5.0
STATUS_TIMEOUT_SEC = 5.0
GEO_TIMEOUT_SEC = 5.0

# ---------------------- Env / Token -----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

# ---------------------- Logging ---------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord_bot")
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
logger.addHandler(file_handler)

# ---------------------- Bot / Intents ---------------
intents = discord.Intents.default()
intents.message_content = True  # required for prefix commands in discord.py v2
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ---------------------- Helpers ---------------------
def _lookup(host: str, port: str):
    """Safely create a JavaServer target."""
    if JavaServer is None:
        raise RuntimeError("mcstatus not installed")
    return JavaServer.lookup(f"{host}:{port}")

def get_server_status(host: str, port: str) -> Dict:
    """
    Basic server status: online flag and player count.
    """
    if JavaServer is None:
        return {"ok": False, "players_online": None, "note": "mcstatus not installed"}

    try:
        socket.setdefaulttimeout(STATUS_TIMEOUT_SEC)
        server = _lookup(host, port)
        s = server.status()
        return {
            "ok": True,
            "players_online": getattr(s.players, "online", 0),
            "raw": s
        }
    except Exception as e:
        return {"ok": False, "players_online": None, "error": str(e)}

def get_player_list(host: str, game_port: str, query_port: Optional[str] = None) -> Dict:
    """
    Try Query (UDP) to fetch player names. If that fails, fall back to Status 'sample' names.
    Requires enable-query=true and UDP port open/forwarded if using Query.
    """
    if JavaServer is None:
        return {"ok": False, "players": [], "note": "mcstatus not installed"}

    use_port = query_port or game_port
    try:
        socket.setdefaulttimeout(QUERY_TIMEOUT_SEC)
        server = _lookup(host, use_port)
        q = server.query()  # may raise if query disabled or UDP blocked
        names: List[str] = q.players.names or []
        return {"ok": True, "players": names, "source": "query"}
    except Exception as query_err:
        # Fallback: status sample
        try:
            socket.setdefaulttimeout(STATUS_TIMEOUT_SEC)
            server = _lookup(host, game_port)
            s = server.status()
            sample = getattr(getattr(s, "players", None), "sample", None) or []
            names = [getattr(p, "name", None) for p in sample if getattr(p, "name", None)]
            if names:
                return {"ok": True, "players": names, "source": "status_sample"}
            return {
                "ok": False,
                "players": [],
                "error": f"Query failed ({query_err}); no sample names in status."
            }
        except Exception as status_err:
            return {
                "ok": False,
                "players": [],
                "error": f"Query failed ({query_err}); status fallback failed ({status_err})."
            }

def geoip_lookup(ip: str) -> Dict:
    """
    GeoIP lookup via ipinfo.io (no key needed for basic usage).
    Returns dict with city, region, country, org when available.
    """
    try:
        url = f"https://ipinfo.io/{ip}/json"
        resp = requests.get(url, timeout=GEO_TIMEOUT_SEC)
        data = resp.json()
        return {
            "ok": True,
            "city": data.get("city", "Unknown"),
            "region": data.get("region", "Unknown"),
            "country": data.get("country", "Unknown"),
            "org": data.get("org", "Unknown"),
            "raw": data
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ---------------------- Commands --------------------
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def roll(ctx, dice: str):
    """Roll dice in NdN format, e.g. /roll 2d6"""
    try:
        rolls, limit = map(int, dice.lower().split("d"))
    except Exception:
        await ctx.send("Format has to be NdN, e.g. 2d6")
        return
    results = [random.randint(1, limit) for _ in range(rolls)]
    await ctx.send(f"🎲 You rolled: {results} → Total: {sum(results)}")

@bot.command()
async def status(ctx):
    """Shows whether the server is online and player count."""
    data = get_server_status(SERVER_IP, SERVER_PORT)
    if data.get("ok"):
        await ctx.send(f"✅ Server is online with {data['players_online']} players!")
    else:
        await ctx.send("⚠️ Server appears to be offline or unreachable.")

@bot.command()
async def players(ctx):
    """
    Lists player names. Uses Query first; falls back to Status sample names.
    Make sure server.properties has enable-query=true and UDP port open if using Query.
    """
    data = get_player_list(SERVER_IP, SERVER_PORT, QUERY_PORT)
    if data.get("ok") and data["players"]:
        source = data.get("source", "unknown")
        await ctx.send(f"👥 Players online ({len(data['players'])}, via {source}): {', '.join(data['players'])}")
    elif data.get("ok"):
        await ctx.send("👥 No player names available right now.")
    else:
        await ctx.send("⚠️ Could not fetch player names. Query may be disabled or UDP blocked.")
        logger.warning(f"/players error: {data.get('error')}")

@bot.command()
async def geo(ctx, ip: str = SERVER_IP):
    """
    Lookup geolocation info for an IP address (default = your server IP).
    """
    res = geoip_lookup(ip)
    if res.get("ok"):
        await ctx.send(
            f"🌍 GeoIP for `{ip}`:\n"
            f"📍 {res['city']}, {res['region']}, {res['country']}\n"
            f"🏢 {res['org']}"
        )
    else:
        await ctx.send(f"⚠️ Could not fetch GeoIP info for {ip}")
        logger.warning(f"/geo error: {res.get('error')}")

# ---------------------- Events ----------------------
@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user}")

# ---------------------- Offline Test Harness --------
def run_offline_tests():
    print("⚙️ Running offline tests…")
    print("Ping test (simulated): Pong!")

    sres = get_server_status(SERVER_IP, SERVER_PORT)
    if sres.get("ok"):
        print(f"Status test: ONLINE, players={sres['players_online']}")
    else:
        print(f"Status test: OFFLINE/ERROR → {sres.get('error') or sres.get('note')}")

    pres = get_player_list(SERVER_IP, SERVER_PORT, QUERY_PORT)
    if pres.get("ok"):
        if pres["players"]:
            print(f"Players test ({pres.get('source')}): {pres['players']}")
        else:
            print("Players test: no names available")
    else:
        print(f"Players test: error → {pres.get('error') or pres.get('note')}")

    gres = geoip_lookup(SERVER_IP)
    if gres.get("ok"):
        print(f"Geo test: {gres['city']}, {gres['region']}, {gres['country']} | {gres['org']}")
    else:
        print(f"Geo test: error → {gres.get('error')}")

    print("✅ Offline tests complete.")

# ---------------------- Main ------------------------
if __name__ == "__main__":
    if not TOKEN:
        print("⚠️ No DISCORD_TOKEN found. Skipping bot.run() and executing offline tests.")
        run_offline_tests()
    else:
        try:
            if "." not in TOKEN or len(TOKEN) < 20:
                raise ValueError("DISCORD_TOKEN does not look valid.")
            bot.run(TOKEN, log_handler=file_handler, log_level=logging.INFO)
        except Exception as e:
            logger.exception("Failed to start bot")
            print(
                f"❌ Could not start bot: {e}\n"
                f"Tip: Create a .env next to this file with:\n"
                f"DISCORD_TOKEN=YOUR_LONG_SECRET_TOKEN"
            )


    
