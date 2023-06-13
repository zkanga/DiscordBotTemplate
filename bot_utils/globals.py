import discord
from discord.ext import commands
import logging
import pytz
import datetime
import sys

channel_name = "bot-commands"
all_alert_role = 'WF Privates Alert'
important_alert_role = "WF Vet Alert"
gruvi_roles = [all_alert_role, important_alert_role]
gruvi_role_colors = [discord.Color(15277667), discord.Color(12745742)]
update_status_time = 5
wf_alert_timer = update_status_time
log_file = "logs/GruVi.log"

intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.members = True
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

# mission keys for the sortie
BOSS_KEY = "boss"
TIME_KEY = "eta"
SORTIE_MISSIONS_KEY = "variants"
MISSION_TYPE_KEY = "missionType"
MISSION_MOD_KEY = "modifier"
MISSION_NODE_KEY = "node"

# Mission keys for the hunt
ARCHON_HUNT_MISSIONS_KEY = "missions"
ARCHON_HUNT_MISSIONS_TYPE_KEY = 'type'
ARCHON_BOSS_NAME_TO_BODY = {
    "Archon Amar": "Wolf Man",
    "Archon Boreal": "Bird(?) Boy",
    "Archon Nira": "Snake Lady",
}

command_prefix = '!'
bot = commands.Bot(command_prefix=command_prefix, intents=intents)

# Set the desired timezone
timezone = pytz.timezone("PST8PDT")

INTERNAL_REWARD_KEY = "Reward"

BASE_PC_API_URL = "https://api.warframestat.us/pc/{loc}?language=en"

DATA_FOLDER = "stored_data"

YAML_TS_KEY = "Timestamp"

NODE_KEY = "node"
#

# See https://warframe.fandom.com/wiki/Invasion for rewards list
BASIC_REWARDS = {'Fieldron', 'Detonite Injector', 'Mutagen Mass', 'Mutalist Alad V Nav Coordinate',

                 "Karak Wraith Blueprint", "Karak Wraith Receiver", "Karak Wraith Stock", "Karak Wraith Barrel",

                 "Latron Wraith Blueprint", "Latron Wraith Receiver", "Latron Wraith Stock", "Latron Wraith Barrel",

                 "Strun Wraith Stock", "Strun Wraith Barrel", "Strun Wraith Receiver", "Strun Wraith Blueprint",

                 "Wraith Twin Vipers Link", "Wraith Twin Vipers Barrel", "Wraith Twin Vipers Receiver",
                 "Wraith Twin Vipers Blueprint",

                 "Sheev Hilt", "Sheev Heatsink", "Sheev Blade", "Sheev Blueprint",

                 "Dera Vandal Stock", "Dera Vandal Barrel", "Dera Vandal Receiver", "Dera Vandal Blueprint",

                 "Snipetron Vandal Blueprint", "Snipetron Vandal Receiver", "Snipetron Vandal Stock",
                 "Snipetron Vandal Barrel"
                 }

# Override default timezone for the logger
logging.Formatter.converter = lambda *args: datetime.datetime.now(tz=timezone).timetuple()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and set the log file path
file_handler = logging.FileHandler(log_file)

# Create a stream handler to log messages to stdout
stream_handler = logging.StreamHandler(sys.stdout)

# Configure the log format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S PST8PDT"
)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the file handler and stream handler to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
