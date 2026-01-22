#  8537827750:AAH7IXmQNNNdX3RQOg4REm5BFnCMYtqjK5s

import random
from http.client import responses

from datetime import datetime
import telebot
from bs4 import BeautifulSoup
import requests
import sqlite3
import threading
import time

# from telegram._utils import markup

# from QuestionsSender import QuestionsSender
# import os

# from telegram._utils import markup

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Вставь сюда токен твоего бота
TOKEN = '8537827750:AAH7IXmQNNNdX3RQOg4REm5BFnCMYtqjK5s'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение и показывает меню."""
    keyboard = [
        [InlineKeyboardButton("Покупаю для себя", callback_data='for_myself')],
        [InlineKeyboardButton("Я дилер", callback_data='dealer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Здравствуйте! Выберите, пожалуйста:', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатия на кнопки."""
    query = update.callback_query
    # Отвечаем на callback, чтобы убрать "часики" в интерфейсе
    await query.answer()

    # Вот тут надо будет вырезать и заменить на нормальную реакцию
    choice = query.data
    if choice == 'for_myself':
        message_text = "Вы выбрали: Покупаю для себя."
    elif choice == 'dealer':
        message_text = "Вы выбрали: Я дилер."

    # Редактируем сообщение, чтобы показать результат выбора
    await query.edit_message_text(text=message_text)

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота в режиме long polling
    application.run_polling()

if __name__ == '__main__':
    main()
