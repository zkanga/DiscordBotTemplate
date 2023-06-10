from datetime import datetime
from datetime import timedelta
from os.path import basename

import discord
from discord.ext import commands
from discord.ext import tasks

from bot_utils.globals import YAML_TS_KEY, bot, logger, update_status_time
from bot_utils.shared_functions import get_api_data
from bot_utils.shared_functions import get_stored_data_file, load_data, dump_data

output_file_name = basename(__file__).replace('.py', '.yaml')
output_file_path = get_stored_data_file(output_file_name)

api_key = "steelPath"
steel_path_key = "Steel"
curr_reward_key = "currentReward"
reward_name_key = "name"
reward_cost_key = "cost"
rotation_key = "rotation"

rewardResetDay = "Sunday"


class SteelPath(commands.Cog):
    """Commands pertaining to the Steel Path"""

    def __init__(self):
        self.bot = bot

    @commands.command(
        help="Gets Steel Path reward rotation based on saved information",
        brief="Gets Steel Path reward rotation",
    )
    async def steelAwards(self, ctx):
        logger.info(f"RECEIVED: Request for Steel Path data")
        await ctx.send(f"{format_output(main())}{ctx.author.mention}")
        logger.info(f"SUCCESS: Completed request for Steel Path data")

    @commands.command(
        help="Requests and saves new steel path reward information and outputs the current rotation",
        brief="Gets Steel Path reward rotation from API",
    )
    async def refreshSteelAwards(self, ctx):
        logger.info(f"RECEIVED: Request for Steel Path data")
        await ctx.send(
            f"{format_output(refreshSteelPathAwards()[steel_path_key])}{ctx.author.mention}")
        logger.info(f"SUCCESS: Completed request for Steel Path data")


@tasks.loop(minutes=update_status_time)
async def set_status():
    logger.info("RECEIVED: Status Update (Steel Path)")
    rewards = get_rewards()
    duration = datetime_to_next_sunday(datetime.utcnow())
    rewards = parse_rewards(rewards)
    currReward = rewards[0]
    hours_left = duration[0] * 24 + duration[1]
    if hours_left < 24:
        scriptDur = f'{((hours_left * 60 + duration[1]) / 60):.1f} hours'
    else:
        scriptDur = f'{(hours_left / 24):.1f} days'
    status = f"{currReward[0]}-{scriptDur}-{currReward[1]} Steel Essence"
    # await bot.change_presence(activity=discord.Game(name=status))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
    logger.info(f"Updated presence to {status}")
    # await bot.change_presence(activity=Activity(type=ActivityType.playing,name=status))
    # logger.info("SUCCESS: Updated status")
    # return status


def get_reward_set(item):
    return [item[reward_name_key], item[reward_cost_key]]


def refreshSteelPathAwards():
    rewardTable = get_api_data(api_key)
    # out = [get_reward_set(rewardTable[curr_reward_key])]
    rotation_rewards = rewardTable[rotation_key]
    curr_reward = rewardTable[curr_reward_key]
    curr_reward_index = rotation_rewards.index(curr_reward)
    out = []
    for item in rotation_rewards[curr_reward_index:] + rotation_rewards[:curr_reward_index]:
        out.append(get_reward_set(item))
    return dump_data(out, steel_path_key, output_file_path)


def datetime_to_next_sunday(time):
    if time.strftime("%A") == rewardResetDay:
        days = 0
    else:
        days = 7 - int(time.strftime("%w"))
    hours = 23 - int(time.strftime("%H"))
    minutes = 59 - int(time.strftime("%M"))
    return [days, hours, minutes]


def format_reward(item):
    return f"{item[0]} ({item[1]} Steel Essence)"


def format_output(rewards):
    timeInfo = datetime_to_next_sunday(datetime.utcnow())
    out = f"Current Reward: ({timeInfo[0]} Days, {timeInfo[1]} Hours, and {timeInfo[2]} Minutes)\n"
    out += f"\t{format_reward(rewards[0])}\n"
    out += f"Next Rewards:\n"
    for reward in rewards[1:]:
        out += f"\t{format_reward(reward)}\n"
    return out


def parse_rewards(data):
    oldTs = data[YAML_TS_KEY]
    nextSunday = datetime_to_next_sunday(oldTs)
    delta = timedelta(hours=nextSunday[1], minutes=nextSunday[2], days=(nextSunday[0] - 7))
    oldTs += delta
    currTs = datetime.utcnow()
    delta = (currTs - oldTs)
    weeksPassed = delta.days // 7
    rewardsToShift = weeksPassed % (len(data[steel_path_key]))
    logger.info(f"{weeksPassed} weeks passed, shifting by {rewardsToShift}")
    output = data[steel_path_key][rewardsToShift:] + data[steel_path_key][:rewardsToShift]
    return output


def get_rewards():
    dat = load_data(steel_path_key, output_file_path, full_dict=True)
    if dat:
        return dat
    else:
        return refreshSteelPathAwards()


def main():
    data = get_rewards()
    return parse_rewards(data)


if __name__ == "__main__":
    main = main()
    print(format_output(main))
    set_status()


