import os
import json


def load_secret():
    base_dir = os.path.abspath(os.path.join(__file__, "../../"))
    if not os.path.exists(base_dir):
        base_dir = os.path.abspath(os.path.join(__file__, "../"))
    with open(os.path.join(base_dir, 'secret.json'), 'rb') as f:
        return json.load(f)


def bot_info(path, bot_tokens):
    bot_dir = os.path.dirname(path)
    bot_dir_name = os.path.basename(bot_dir)
    bot_idx = int(bot_dir_name.split('_')[-1])
    return bot_tokens[bot_idx]