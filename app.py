import os
import io
import datetime
import logging

import requests
from flask import Flask, request
from dotenv import load_dotenv

from settings import IS_PRIVATE, BASE_URL, WEBHOOK_URL, WEBHOOK_PATH, FILE_URL
from send import send_to_admin, send_message, edit_message_text, send_document
from invoice_parser import Invoices, Export

# from invoice_parser.invoices import Invoices
# from invoice_parser.export import Export


load_dotenv()

logging.basicConfig(
    filename="bot.log" ,
    level="INFO",format='%(asctime)s::%(name)s::%(levelname)s::%(message)s [%(filename)s:%(lineno)d]',
    datefmt='%d-%b-%y %H:%M:%S')


webhook = Flask(__name__)


@webhook.route(WEBHOOK_PATH, methods=["POST"])
def hook():
    if request.headers['X-Telegram-Bot-Api-Secret-Token'] != os.environ.get("SECRET"):
        logging.critical("Invalid secret_token")
        return "Invalid Secret Token"

    data = request.json

    is_message = data.get("message", None)

    if not is_message:
        logging.debug(f"Not a Message: {request.data}")
        return "Not a message"

    chat_id = data['message']['chat']['id']
    first_name = data['message']['chat']['first_name']
    last_name = data['message']['chat']['last_name']
    username = data['message']['chat'].get('username', None)

    has_document = data["message"].get("document")
    has_text = data["message"].get("text")

    allowed_list = os.environ.get("ALLOWED_LIST", "").split(",")

    if IS_PRIVATE and (str(chat_id) in allowed_list or (username and  username in allowed_list)):
        if not has_document:
            if has_text:
                send_message(chat_id, f"Hello, {first_name} {last_name}\nPlease send a vyapar pdf invoice.")
                return "OK"
            media = ["photo", "video", "audio", "video_note", "voice", "location", "poll", "contact"]
            for m in media:
                if m in data["message"]:
                    send_message(chat_id, f"can't process {m}. Only PDF files are allowed.")
                    return "OK"
            return "OK"


        document = has_document

        file_name:str = document['file_name']

        if not file_name.endswith('.pdf'):
            send_message(chat_id, f"can't process {file_name.split('.')[-1].upper()} files. Only PDF files are allowed.")
            return "OK"

        file_name = file_name[:-4]
        file_id = document['file_id']

        temp_file_name = "temp/" + file_name + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".xlsx"

        msg = send_message(chat_id, "getting file info...")

        msg_id = msg.json()["result"]["message_id"]

        get_file = requests.get(f"{BASE_URL}/getFile", {"file_id": file_id})


        if get_file.ok:
            file_path = FILE_URL + "/" + get_file.json()['result']['file_path']

            edit_message_text(chat_id, msg_id, "downloading file...")

            file = requests.get(file_path)

            if file.ok:
                start_time = datetime.datetime.now().timestamp()
                edit_message_text(chat_id, msg_id, "parsing...")

                try:
                    invoices = Invoices(io.BytesIO(file.content))
                except Exception as e:
                    logging.error(e)
                    edit_message_text(chat_id,msg_id, f"❌ invalid pdf: either pdf is corrupt or not a vyapar PDF invoice.")
                    return "OK"

                edit_message_text(chat_id, msg_id, "exporting...")

                export = Export(invoices.table)
                export.save(temp_file_name)

                edit_message_text(chat_id, msg_id, f"Done ✅ in {round(datetime.datetime.now().timestamp()-start_time, 2)} seconds")

                # send_message(chat_id, f"It took {round(datetime.datetime.now().timestamp()-start_time, 2)} seconds.")
                sent = send_document(chat_id, (file_name+".xlsx", open(temp_file_name, "rb")))

                if sent.ok:
                    os.remove(temp_file_name)
                    send_message(chat_id, f"Files: {file_name}.pdf, {file_name}.xlsx removed from server. ✅")
                    send_message(chat_id, "if you find any errors please contact admin.")
                else:
                    send_message(chat_id, "something went wrong. please, contact admin.")
                    logging.error("Document sent error" + sent.text)
                    return "OK"


            else:
                logging.error("error downloading input pdf file" + file.text)
                edit_message_text(chat_id, msg_id, "❌ download file not found. Please, contact admin.")
                return "OK"
        else:
            edit_message_text(chat_id, msg_id, "❌ file info not found. Please, contact admin.")
            logging.error("error getting file path")
            return "OK"

    else:
        send_message(chat_id,
                     f"Hello, {first_name} {last_name}\nYou are not allowed to use this bot. Please contact admin.")

    return "OK"


def run_app():
    logging.info("Webhook started")
    webhook.run()


# setWebhook
webhook_setup = requests.post(f"{BASE_URL}/setWebhook",
                              {"url": f"{WEBHOOK_URL}{WEBHOOK_PATH}", "secret_token": os.environ.get("SECRET"),
                               "drop_pending_updates": True})


if __name__ == '__main__':
    if webhook_setup.ok:
        logging.info(f"Webhook setup done : {webhook_setup.text}")
        run_app()
    else:
        logging.error(webhook_setup.text)
        send_to_admin(webhook_setup.text)

