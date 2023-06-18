import os
from dotenv import load_dotenv
load_dotenv()


__BASE_URI = "https://api.telegram.org"

BOT_TOKEN = f"bot{os.environ.get('TOKEN')}"

BASE_URL = f"{__BASE_URI}/{BOT_TOKEN}"
FILE_URL = f"{__BASE_URI}/file/{BOT_TOKEN}"

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH")

IS_PRIVATE=os.environ.get("IS_PRIVATE", False)
