from discord.ext import commands

from bot_utils.globals import bot, logger, BOSS_KEY, TIME_KEY, ARCHON_HUNT_MISSIONS_KEY, \
    ARCHON_HUNT_MISSIONS_TYPE_KEY, ARCHON_BOSS_NAME_TO_BODY

from bot_utils.shared_functions import get_api_data, flatten_list


class ArchonHunt(commands.Cog):
    """Commands for archon hunt information"""

    def __init__(self):
        self.bot = bot

    @commands.command(
        brief="Sends current archon hunt info",
    )
    async def archonHunt(self, ctx):
        dat = get_archon_hunt()
        if dat:
            await ctx.send(f"{dat[TIME_KEY]}\n{flatten_list(dat[ARCHON_HUNT_MISSIONS_KEY], True, True)}"
                           f"{ctx.author.mention}")
            logger.info(f"COMPLETE: Provided archon hunt data")
        else:
            await ctx.send(f"Sorry but we could not provide archon hunt data\n{ctx.author.mention}")


def get_archon_hunt():
    response = get_api_data("archonHunt")
    if not response:
        return response
    out = {ARCHON_HUNT_MISSIONS_KEY: []}
    for mission in response[ARCHON_HUNT_MISSIONS_KEY]:
        if mission[ARCHON_HUNT_MISSIONS_TYPE_KEY] == "Assassination":
            archon = response[BOSS_KEY]
            boss_body = ARCHON_BOSS_NAME_TO_BODY.get(archon)
            out[ARCHON_HUNT_MISSIONS_KEY].append(f"{mission[ARCHON_HUNT_MISSIONS_TYPE_KEY]}({archon})")
            out[TIME_KEY] = f"Hunt the {boss_body} for the next {response[TIME_KEY].replace('-', '')}"
        else:
            out[ARCHON_HUNT_MISSIONS_KEY].append(f"{mission[ARCHON_HUNT_MISSIONS_TYPE_KEY]}")
    return out

