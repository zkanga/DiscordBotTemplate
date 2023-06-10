from datetime import datetime

from bot_utils.globals import NODE_KEY, INTERNAL_REWARD_KEY, YAML_TS_KEY


class NodeReward:
    def __init__(self, node_id, node, rewards):
        self.id = node_id
        self.node = node
        self.rewards = sorted(rewards)
        self.detected_ts = datetime.utcnow()

    def __str__(self):
        rewards = str(self.rewards).replace("[", "").replace("]", "").replace("'", "")
        return f'{self.node} - {rewards}'

    def get_log_node_dat(self):
        return {
            NODE_KEY: self.node,
            INTERNAL_REWARD_KEY: self.rewards,
            YAML_TS_KEY: self.detected_ts
        }
