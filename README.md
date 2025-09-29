# Discord-Bot-Project-Payton-Shawn-Caleb
GitHub used for Discord Bot Project

- Once we get functionaility of bot complete please input how the bot works, followed with commands
- Dont have to be detailed really, we have to write a analysis anyways
1. /ping
Complexity: S


Activation: Slash command.


How it works: When triggered, the bot sends a simple response to confirm it is alive. For one user ID, the response is a humorous Easter egg (“Cheese Pizza!”).


Community Value: Provides a quick way to confirm the bot is responsive without relying on other commands.


2. /status
Complexity: L


Activation: Slash command.


How it works: The bot queries the Minecraft server using mcstatus.JavaServer.lookup(). It attempts to fetch server status, player counts, and names of currently online players. If the server is down, it returns “Server is offline.” If the server is online but doesn’t return player names, it still reports the number of players.


Community Value: Saves members from launching Minecraft to check server availability, enabling quick decisions about when to play.


3. /serverinfo
Complexity: S


Activation: Slash command.


How it works: Displays the server IP and port in formatted text.


Community Value: New players can easily copy connection details from Discord instead of repeatedly asking administrators.


4. /shutdown
Complexity: M


Activation: Slash command, restricted by user ID to the bot owner.


How it works: If called by the authorized owner, the bot sends a shutdown message, closes the Discord connection, and exits the Python process. Unauthorized users receive a denial message.


Community Value: Allows the server administrator to shut down or restart the bot safely for updates and maintenance without manual process management.


5. /Jointeam
Complexity: L


Activation: Slash command


How it works: 


Community Value:.
