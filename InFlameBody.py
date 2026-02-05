#  8537827750:AAH7IXmQNNNdX3RQOg4REm5BFnCMYtqjK5s

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Вставь сюда токен твоего бота
TOKEN = '8537827750:AAH7IXmQNNNdX3RQOg4REm5BFnCMYtqjK5s'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для отслеживания, где находится пользователь
USER_STATE = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение и показывает главное меню."""
    keyboard = [
        [InlineKeyboardButton("Покупаю для себя", callback_data='for_myself')],
        [InlineKeyboardButton("Я дилер", callback_data='dealer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Здравствуйте! Выберите, пожалуйста:', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатия на кнопки."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    choice = query.data

    # --- Обработка первого уровня ---
    if choice == 'for_myself':
        await query.edit_message_text(text="Вы выбрали: Покупаю для себя.")
    elif choice == 'dealer':
        keyboard = [
            [InlineKeyboardButton("Новый дилер", callback_data='new_dealer')],
            [InlineKeyboardButton("Уже работаем вместе", callback_data='existing_dealer')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Я дилер.", reply_markup=reply_markup)

    # --- Обработка второго уровня для дилера ---
    elif choice == 'new_dealer':
        keyboard = [
            [InlineKeyboardButton("Юридическое лицо", callback_data='entity_legal')],
            [InlineKeyboardButton("ИП", callback_data='entity_ip')],
            [InlineKeyboardButton("Физическое лицо (самозанятый)", callback_data='entity_self')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите форму организации:", reply_markup=reply_markup)
    elif choice == 'existing_dealer':
        await query.edit_message_text(text="Спасибо! Мы свяжемся с вами.")

    # --- Обработка третьего уровня для юрлица ---
    elif choice == 'entity_legal':
        USER_STATE[user_id] = 'waiting_for_company_name'
        await query.edit_message_text(text="Напишите ваш ИНН:")
    elif choice == 'entity_ip':
        USER_STATE[user_id] = 'waiting_for_details_ip'
        await query.edit_message_text(text="Спасибо! Пожалуйста, укажите ваши данные для связи и реквизиты ИП.")
    elif choice == 'entity_self':
        USER_STATE[user_id] = 'waiting_for_details_self'
        await query.edit_message_text(text="Спасибо! Пожалуйста, укажите ваши данные для связи и информацию о самозанятости.")


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ввод текста, например, ИНН."""
    user_id = update.effective_message.from_user.id
    text = update.effective_message.text.strip()

    if USER_STATE.get(user_id) == 'waiting_for_inn':
        # Просто подтверждаем получение ИНН, не проверяя его
        if not text.isdigit():
            await update.effective_message.reply_text("Пожалуйста, введите корректный ИНН (цифры).")
            return

        inn = text
        await update.effective_message.reply_text(f"Спасибо! Ваш ИНН: {inn}. Мы свяжемся с вами для обсуждения условий сотрудничества.")
        # Сброс состояния после обработки
        USER_STATE.pop(user_id, None)
    
    # Заглушка для ИП
    elif USER_STATE.get(user_id) == 'waiting_for_details_ip':
        await update.effective_message.reply_text("Спасибо за предоставленную информацию! Мы свяжемся с вами для обсуждения условий сотрудничества.")
        USER_STATE.pop(user_id, None)

    # Заглушка для физлица
    elif USER_STATE.get(user_id) == 'waiting_for_details_self':
        await update.effective_message.reply_text("Спасибо за предоставленную информацию! Мы свяжемся с вами для обсуждения условий сотрудничества.")
        USER_STATE.pop(user_id, None)


def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    application.run_polling()

if __name__ == '__main__':
    main()
