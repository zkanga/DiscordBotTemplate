from datetime import datetime
from os.path import exists
from pathlib import Path

import requests
import yaml

from bot_utils.globals import BASE_PC_API_URL, DATA_FOLDER, YAML_TS_KEY, logger


def get_stored_data_file(name):
    return Path(__file__).parent.parent.joinpath(DATA_FOLDER).joinpath(name)


def dump_data(data, subject, loc):
    out = {subject: data, YAML_TS_KEY: datetime.utcnow()}
    with open(loc, 'w') as out_stream:
        yaml.dump(out, out_stream, default_flow_style=False)
        logger.info(f"SUCCESS: Logged output to {loc}")
    return out


def load_data(subject, loc, default=False, full_dict=False):
    if exists(loc):
        with open(rf"{loc}", 'r') as file:
            data = yaml.safe_load(file)
            if data is not None and data:
                keys = sorted(set(data.keys()))
                if sorted({YAML_TS_KEY, subject}) == keys:
                    logger.info(f"SUCCESS: Loaded {subject} data from yaml")
                    if full_dict:
                        return data
                    return data[subject]
    if not isinstance(default, bool) or default:
        logger.error(f"ERROR: Returning default. Couldn't read {subject}")
        return default
    logger.error(f"ERROR: Couldn't read {subject} data")
    return False


def get_api_data(area):
    try:
        url = BASE_PC_API_URL.replace("{loc}", area)
        response = requests.get(url).json()
        logger.info(f"SUCCESS: Got {area} data")
    except Exception as e:
        logger.error(f"ERROR: Couldn't get data from api:\n{e}")
        return False
    return response


def flatten_list(list_name, multi_line: bool, trailing_delim: bool = True):
    out = ""
    if multi_line:
        joiner = '\n'
    else:
        joiner = ' '
    for item in list_name:
        out += item + joiner
    if trailing_delim:
        return out
    else:
        return out[:-1]
