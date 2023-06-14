from discord.ext import commands

from bot_utils.globals import bot, logger, BOSS_KEY, TIME_KEY, SORTIE_MISSIONS_KEY, \
    MISSION_TYPE_KEY, MISSION_MOD_KEY, MISSION_NODE_KEY

from bot_utils.shared_functions import get_api_data, flatten_list


class Sortie(commands.Cog):
    """Commands for sortie information"""

    def __init__(self):
        self.bot = bot

    @commands.command(
        brief="Sends current sortie info",
    )
    async def sortie(self, ctx):
        logger.info(f"RECEIVED: request for sortie data")
        dat = get_all_sorties()
        if dat:
            await ctx.send(
                f"{flatten_list(dat[SORTIE_MISSIONS_KEY], True, True) + dat[TIME_KEY]}\n{ctx.author.mention}")
            logger.info(f"COMPLETE: Provided sortie data")
        else:
            await ctx.send(f"Sorry but we could not provide sortie data\n{ctx.author.mention}")


def get_all_sorties():
    response = get_api_data("sortie")
    if not response:
        return response
    out = {TIME_KEY: f"For the next {response[TIME_KEY].replace('-', '')}",
           SORTIE_MISSIONS_KEY: []}
    for mission in response[SORTIE_MISSIONS_KEY]:
        if mission[MISSION_TYPE_KEY] == "Assassination":
            out[SORTIE_MISSIONS_KEY].append(
                f"{mission[MISSION_TYPE_KEY]}({response[BOSS_KEY]}) - {mission[MISSION_MOD_KEY]}")
        elif "Lua" in mission[MISSION_NODE_KEY] and mission[MISSION_TYPE_KEY] == 'Spy':
            hate = f"\n\nWATCH THE FLIP OUT\n\n" \
                   f"Lua Spy with {mission[MISSION_MOD_KEY]}\n" \
                   f"All my homies hate Lua Spies with {mission[MISSION_MOD_KEY]}"
            out[SORTIE_MISSIONS_KEY].append(hate)
        else:
            out[SORTIE_MISSIONS_KEY].append(f"{mission[MISSION_TYPE_KEY]} - {mission[MISSION_MOD_KEY]}")
    return out
