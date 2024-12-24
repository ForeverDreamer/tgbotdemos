import os
from share.utils.misc import load_secret

secret = load_secret()

MONGO_URI = os.getenv(
    'MONGO_URI',
    f"mongodb://root:{secret['mongodb_pwd']['encoded']}@mongo1:17017,mongo2:17018,mongo3:17019/tgbot?replicaSet=rs0&authSource=admin"
)

WEB_HOST = secret['web_host']
REDIS_URI = os.getenv('REDIS_URI', f"redis://{secret['rds_host']}:16379/0")

BOT_TOKENS = secret['bot_tokens']
# BOT_TOKENS_DIC = {}
# for token in secret['bot_tokens']:
#     k, v = token.split('')
#     BOT_TOKENS.append((k, v))
#     BOT_TOKENS_DIC[k] = v
APPS = secret['apps']

ETHERSCAN_API_KEY = secret['etherscan_api_key']

ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"

AWAIT_INPUT = 1
