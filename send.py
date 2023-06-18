import os

from requests import post
from settings import BASE_URL


SEND_MESSAGE_URL = f"{BASE_URL}/sendMessage"
EDIT_MESSAGE_URL = f"{BASE_URL}/editMessageText"
SEND_DOCUMENT_URL = f"{BASE_URL}/sendDocument"
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

def send_to_admin(msg):
    return post(SEND_MESSAGE_URL, {'chat_id': ADMIN_CHAT_ID, "text": msg})


def send_message(chat_id, message):
    # try:
    return post(SEND_MESSAGE_URL, {"chat_id": chat_id, "text": message})
    # except Exception as e:
    #     logging.error(e)
    #
    #     return


def edit_message_text(chat_id, msg_id, text):
    # try:
    return post(EDIT_MESSAGE_URL, {"chat_id": chat_id, "message_id": msg_id, "text": text})
    # except Exception as e:
    #     logging.error(e)
    #     return

def send_document(chat_id, document):
    # try:
    return post(SEND_DOCUMENT_URL, {"chat_id": chat_id}, files={"document":document})
    # except Exception as e:
    #     logging.error(e)
    #     return
