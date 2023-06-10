from os.path import basename

from discord.ext import commands
from discord.ext import tasks

from commands_code.utils.NodeReward import NodeReward
from bot_utils.bot_notifications import ping_in_all_bot_commands
from bot_utils.globals import bot, logger, wf_alert_timer, NODE_KEY, BASIC_REWARDS, gruvi_roles, all_alert_role
from bot_utils.shared_functions import get_api_data, get_stored_data_file, load_data, dump_data

ALERT_API_KEY = "alerts"
INVASION_API_KEY = "invasions"

ACTIVE_KEY = 'active'
ALERT_MISSION_KEY = 'mission'
ALERT_REWARD_KEY = 'reward'
ALERT_ITEMS_KEY = 'itemString'
ALERT_ID_KEY = 'id'

COMPLETED_INVASION_KEY = "completed"
REWARDS_LIST_KEYS = ["attackerReward", "defenderReward"]
REWARD_ITEM_ITR_KEY = 'countedItems'
REWARD_ITEM_TYPE = 'type'
INVASION_ID_KEY = 'id'

output_file_name = basename(__file__).replace('.py', '.yaml')
output_file_path = get_stored_data_file(output_file_name)


class WarframeEvents(commands.Cog):
    """Commands pertaining to drops from special warframe missions (Alerts and Invasions)"""

    def __init__(self):
        self.bot = bot

    @commands.command(
        brief="Sends all current events with a non-standard reward",
    )
    async def getEvents(self, ctx):
        logger.info(f"RECEIVED: Request for Alert data")
        out_str = await alert_body(False)
        if out_str and isinstance(out_str, str):
            await ctx.send(f"{out_str}\n{ctx.author.mention}")
        else:
            await ctx.send(f"There are no active events with drops\n{ctx.author.mention}")
        logger.info(f"SUCCESS: Completed request for alert data")


@tasks.loop(minutes=wf_alert_timer)
async def warframe_event_notifications():
    logger.info("RECEIVED: Request to ping for new alerts")
    out_str, rare = await alert_body(True)
    if out_str and isinstance(out_str, str) and rare:
        await ping_in_all_bot_commands(out_str, gruvi_roles)
    if out_str and isinstance(out_str, str) and rare is False:
        await ping_in_all_bot_commands(out_str, [all_alert_role])
    logger.info("SUCCESS: Checked for new alerts")


def dump_warframe_alert_dat():
    return dump_data(PREVIOUSLY_DETECTED_ALERTS, ALERT_API_KEY, output_file_path)


def parse_alerts(dat):
    nodes = list()
    for curr_alert in dat:
        if curr_alert[ACTIVE_KEY]:
            possible_rewards = [curr_alert[ALERT_MISSION_KEY][ALERT_REWARD_KEY][ALERT_ITEMS_KEY]]
            nodes.append(
                NodeReward(curr_alert[ALERT_ID_KEY], curr_alert[ALERT_MISSION_KEY][NODE_KEY], possible_rewards)
            )
    return nodes


def filter_bad_alerts(alert_nodes):
    output_nodes = []
    for node in alert_nodes:
        keep = False
        for reward in node.rewards:
            if reward not in BASIC_REWARDS:
                keep = True
        if keep:
            output_nodes.append(node)
    return output_nodes


def process_output(nodes, only_new):
    ping_nodes = []
    out_str = ""
    if only_new:
        for node in nodes:
            if node.id in PREVIOUSLY_DETECTED_ALERTS.keys():
                logger.info(f"Detected {node} again. Ignoring it")
            else:
                ping_nodes.append(node)
                out_str += f"{str(node)}\n"
    else:
        ping_nodes = nodes
        for node in nodes:
            out_str += f"{str(node)}\n"
    return ping_nodes, out_str


def detect_important_drop(alert_nodes):
    for node in alert_nodes:
        for reward in node.rewards:
            if reward not in BASIC_REWARDS:
                return True
    return False


def parse_invasions(invasions):
    nodes = list()
    for curr_invasion in invasions:
        # Ignores invasions which are completed
        if not curr_invasion[COMPLETED_INVASION_KEY]:
            possible_rewards = []
            for faction_in_invasion in REWARDS_LIST_KEYS:
                faction_rewards = curr_invasion[faction_in_invasion]
                curr_rewards = faction_rewards[REWARD_ITEM_ITR_KEY]
                for reward_item in curr_rewards:
                    possible_rewards.append(reward_item[REWARD_ITEM_TYPE])
            nodes.append(NodeReward(curr_invasion[INVASION_ID_KEY], curr_invasion[NODE_KEY], possible_rewards))
    return nodes


async def alert_body(only_new):
    alert_dat = get_api_data(ALERT_API_KEY)
    invasion_dat = get_api_data(INVASION_API_KEY)
    nodes = parse_alerts(alert_dat) + parse_invasions(invasion_dat)
    nodes_to_return, out_str = process_output(nodes, only_new)
    if out_str != "":
        out_str = out_str[:-1]
        if only_new:
            has_important_drop = detect_important_drop(nodes_to_return)
            for node in nodes_to_return:
                PREVIOUSLY_DETECTED_ALERTS[node.id] = node.get_log_node_dat()
            dump_warframe_alert_dat()
            return out_str, has_important_drop
        else:
            return out_str
    return False, False

PREVIOUSLY_DETECTED_ALERTS = load_data(ALERT_API_KEY, output_file_path, dict())
