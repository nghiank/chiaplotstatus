import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler

import pyscreenshot as ImageGrab
import os
import time


def send(msg, chat_id='-549746545', token='1824677693:AAEOnTrhcE5Lert8h1sHsyU_jBFWfpYRvyw'):
    """
    Send a message to a telegram user or group specified on chatId
    chat_id must be a number!
    """
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)

def capture(update, context):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("\aHeads up! new screenshot in 2 seconds : " + dir_path)
    time.sleep(2)
    im = ImageGrab.grab()
    im.save(dir_path + "/screen2.png", "PNG")
    print("Sending...")
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open(dir_path + '/screen2.png', 'rb'), filename='abc')
    print("Sent")

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="LoL!")

def start_listen_telegram(chat_id='-549746545', token='1824677693:AAEOnTrhcE5Lert8h1sHsyU_jBFWfpYRvyw'):
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    capture_handler = CommandHandler('capture', capture)
    dispatcher.add_handler(capture_handler)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    print("Running bot now.")
    updater.start_polling()
