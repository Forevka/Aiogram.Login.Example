from os import getenv

ENVIRONMENT = getenv("env", "debug")

BOT_TOKEN = getenv("bot_token", "Aa:123")
HOST_URL = getenv("host_url", "")