from os.path import basename

from discord.ext import commands
from requests import get

from bot_utils.globals import bot, logger
from bot_utils.shared_functions import get_stored_data_file
from bot_utils.shared_functions import load_data, dump_data

output_file_name = basename(__file__).replace('.py', '.yaml')
output_file_path = get_stored_data_file(output_file_name)
VAULTED_RELICS_KEY = "Vaulted Relics"

# URL TO SCRAP
vaulted_relics_url = "https://warframe.fandom.com/wiki/Category:Relic"

# REGEX FLAGS
vaulted_open_flag = "title=\""
vaulted_close_flag = "\""
frame_flag = "/"


class VaultedRelics(commands.Cog):
    """Commands pertaining to vaulted relics"""

    def __init__(self):
        self.bot = bot

    @commands.command(
        brief="Gets saved vaulted parts",
    )
    async def vaultedRelics(self, ctx):
        parts = get_vaulted_relics()
        if parts:
            await ctx.send(f"{format_vaulted(list(parts[VAULTED_RELICS_KEY]))}\n{ctx.author.mention}")
        else:
            await ctx.send(f"{parts}\n{ctx.author.mention}")
        logger.info(f"COMPLETE: Request for vaulted parts data")

    @commands.command(
        help="Downloads and parsers fresh data from the wiki for the latest vaulted parts",
        brief="Gets vaulted parts from the wiki",
    )
    async def refreshVaultedRelics(self, ctx):
        parts = build_vaulted_relics_yaml()
        if parts:
            await ctx.send(f"{format_vaulted(list(parts[VAULTED_RELICS_KEY]))}\n{ctx.author.mention}")
        else:
            await ctx.send(f"{parts}\n{ctx.author.mention}")
        logger.info(f"COMPLETE: Request refreshed vaulted parts data")


def parse_vaulted_parts(line):
    opener = line.rfind(vaulted_open_flag) + len(vaulted_open_flag)
    closer = line.find('"', opener)
    if opener != -1 and closer != -1:
        title_value = line[opener:closer]
        return title_value
    else:
        logger.error(f"Can't parse {line}")


def build_vaulted_relics_yaml():
    relics = scrape_vaulted_relics()
    if relics:
        return dump_data(relics, VAULTED_RELICS_KEY, output_file_path)
    return relics


def get_vaulted_relics():
    out = load_data(VAULTED_RELICS_KEY, output_file_path, full_dict=True)
    if out:
        return out
    return build_vaulted_relics_yaml()


def scrape_vaulted_relics():
    vaultedItems = set()
    try:
        vaultedWebPage = get(vaulted_relics_url, 'html.parser').text
    except Exception as e:
        logger.error(f"ERROR: Couldn't reach the wiki page:\n\t{e}")
        return f"Couldn't reach the wiki page:\n"
    logger.info("SUCCESS: Read wiki page")
    vaultedWebPage = vaultedWebPage.split('\n')
    for line in vaultedWebPage:
        if ("href=\"/wiki/Lith_" in line or
            "href=\"/wiki/Meso_" in line or
            "href=\"/wiki/Neo_" in line or
            "href=\"/wiki/Axi_"in line ) and "title=\""  in line:
            vaultedItems.add(parse_vaulted_parts(line))
    return vaultedItems


def format_vaulted(vaulted_list):
    vaultedItems = vaulted_list
    vaultedItems.sort()
    out = '\n'.join(item for item in vaultedItems)
    return out
