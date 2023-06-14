# Python Discord Bot Template

## General Information
A WIP template of a bot which can be used to relatively quickly create custom discord bots off of a flexible base
To demonstrate the functionality of the code, this repo is currently populated with commands relating to the Warframe Game


## Helpful commands
### Innate commands include:
* cleanUp:                Removes all commands for and messages from this bot
* addRole:                Assign a role to yourself or another
* dropRole:               Remove a role to yourself or another
* roles:                  Prints all roles available via this bot

### Utility functions:
* dump_data: Stores data in a yaml file under stored_data (in bot_utils.shared_functions)
* load_data: Reads data in a yaml file under stored_data (in bot_utils.shared_functions)
* ping_in_all_bot_commands: pings a role(s) under all servers (in bot_utils.bot_notifications)
* ping_in_guild: pings a role(s) in a specific guild (in bot_utils.bot_notifications)

## Quick Deployment
Copy the repo and deploy the test version of the bot with the following commands:
```
git clone https://github.com/zkanga/DiscordBotTemplate.git
 ~/DiscordBotTemplate/manuals/deployment.sh --bot_name "Bot Name" --bot_key "Key Value" --user_name "$whoami"
```