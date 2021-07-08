import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler

import os
import time


def send(msg, chat_id='-549746545', token='1824677693:AAEOnTrhcE5Lert8h1sHsyU_jBFWfpYRvyw'):
    """
    Send a message to a telegram user or group specified on chatId
    chat_id must be a number!
    """
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)

