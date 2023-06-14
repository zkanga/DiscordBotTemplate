from bot_utils.globals import logger, bot, command_prefix
from commands_code.steel_path import SteelPath, set_status
from commands_code.warframe_events import WarframeEvents, warframe_event_notifications
from commands_code.sortie_info import Sortie
from commands_code.archon_hunt import ArchonHunt
from commands_code.vaulted_prime_parts import VaultedPrimeParts
from commands_code.unvaulted_relics import UnvaultedRelics
from bot_utils.bot_notifications import BotNotifications
import os

# from bot_utils.clean_up import cleanUp

# Import url
# https://discord.com/oauth2/authorize?client_id=1114966749281013782&permissions=40667958476400&scope=bot

cogs = [
    SteelPath()
    , Sortie()
    , VaultedPrimeParts()
    , WarframeEvents()
    , BotNotifications()
    , ArchonHunt()
    , UnvaultedRelics()
]

routines = [
    set_status
    , warframe_event_notifications
]


async def setup():
    for cog in cogs:
        await bot.add_cog(cog)
        logger.info(f"SUCCESS: Added {cog.qualified_name} cog")
    for routine in routines:
        routine.start()


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')
    await setup()
    logger.info(f'SUCCESS: Set up {bot.user.name}')


@bot.command()
async def cleanUp(ctx):
    f"""Removes all messages sent by me in the channel"""
    all_cmds = []
    for command in bot.walk_commands():
        all_cmds.append(f"{command_prefix}{command.name}")
    # invocations = [command_prefix + item for item in list(bot.commands)]

    starts_with_any = lambda string, prefixes: any(string.startswith(prefix) for prefix in prefixes)

    def is_bot_message(message):
        return message.author == bot.user or starts_with_any(message.content, all_cmds)

    deleted_messages = await ctx.channel.purge(limit=None, check=is_bot_message)
    logger.info(f"Deleted {len(deleted_messages)} messages in {ctx.channel.name}")


bot.run(os.environ.get('bot_key'))
