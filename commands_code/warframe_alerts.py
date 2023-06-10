from os.path import basename

from discord.ext import commands
from discord.ext import tasks

from commands_code.utils.NodeReward import NodeReward
from bot_utils.bot_notifications import ping_in_all_bot_commands
from bot_utils.globals import bot, logger, wf_alert_timer, NODE_KEY, BASIC_REWARDS, important_alert_role, all_alert_role
from bot_utils.shared_functions import get_api_data, get_stored_data_file, load_data, dump_data

API_KEY = "alerts"
ACTIVE_KEY = 'active'
ALERT_MISSION_KEY = 'mission'
ALERT_REWARD_KEY = 'reward'
ALERT_ITEMS_KEY = 'items'
ALERT_ID_KEY = 'id'

output_file_name = basename(__file__).replace('.py', '.yaml')
output_file_path = get_stored_data_file(output_file_name)


class WarframeAlerts(commands.Cog):
    """Commands pertaining to warframe alerts"""

    def __init__(self):
        self.bot = bot

    @commands.command(
        brief="Sends all current alerts with a non-standard reward",
    )
    async def getAlerts(self, ctx):
        logger.info(f"RECEIVED: Request for Alert data")
        out_str = await alert_body(False)
        if out_str:
            await ctx.send(f"{out_str}{ctx.author.mention}")
        else:
            await ctx.send(f"There are no alerts with non-standard drops\n{ctx.author.mention}")
        logger.info(f"SUCCESS: Completed request for alert data")


def dump_warframe_alert_dat():
    return dump_data(PREVIOUSLY_DETECTED_ALERTS, API_KEY, output_file_path)


@tasks.loop(minutes=wf_alert_timer)
async def warframe_alert_notifications():
    logger.info("RECEIVED: Request to ping for new alerts")
    await alert_body(True)
    logger.info("SUCCESS: Checked for new alerts")


def parse_alerts(dat):
    nodes = list()
    for curr_alert in dat:
        if curr_alert[ACTIVE_KEY]:
            possible_rewards = curr_alert[ALERT_MISSION_KEY][ALERT_REWARD_KEY][ALERT_ITEMS_KEY]
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


def detect_rare_drop(alert_nodes):
    for node in alert_nodes:
        for reward in node.rewards:
            if reward not in BASIC_REWARDS:
                return True
    return False


async def alert_body(only_new):
    dat = get_api_data(API_KEY, logger)
    alert_nodes = parse_alerts(dat)
    # alert_nodes = filter_bad_alerts(alert_nodes)
    has_rare_drop = detect_rare_drop(alert_nodes)
    alert_nodes, out_str = process_output(alert_nodes, only_new)
    if out_str != "":
        out_str = out_str[:-1]
        if only_new:
            if has_rare_drop:
                await ping_in_all_bot_commands(out_str, important_alert_role)
            elif has_rare_drop is False:
                await ping_in_all_bot_commands(out_str, all_alert_role)
            for node in alert_nodes:
                PREVIOUSLY_DETECTED_ALERTS[node.id] = node.get_log_node_dat()
            dump_warframe_alert_dat()
            return out_str
        else:
            return out_str
    return False


# async def alert_body_old(only_new):
#     dat = get_api_data(API_KEY, logger)
#     alert_nodes = parse_alerts(dat)
#     alert_nodes = filter_bad_alerts(alert_nodes)
#     alert_nodes, out_str = process_output(alert_nodes, only_new)
#     if out_str != "":
#         out_str = out_str[:-1]
#         if only_new:
#
#             await ping_in_bot_commands(out_str)
#             for node in alert_nodes:
#                 PREVIOUSLY_DETECTED_ALERTS[node.id] = node.get_log_node_dat()
#             dump_warframe_alert_dat()
#             return out_str
#         else:
#             return out_str
#     return False


PREVIOUSLY_DETECTED_ALERTS = load_data(API_KEY, output_file_path, dict())
