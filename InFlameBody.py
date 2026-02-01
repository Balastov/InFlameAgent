#  8537827750:AAH7IXmQNNNdX3RQOg4REm5BFnCMYtqjK5s

import logging
import requests
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
        USER_STATE[user_id] = 'waiting_for_inn'
        await query.edit_message_text(text="Напишите ваш ИНН:")
    elif choice in ['entity_ip', 'entity_self']:
        # Для простоты, другие типы сразу завершаются
        await query.edit_message_text(text=f"Выбрана форма: {choice.replace('entity_', '').title()}. Скоро с вами свяжутся.")


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ввод текста, например, ИНН."""
    user_id = update.effective_message.from_user.id
    text = update.effective_message.text.strip()

    if USER_STATE.get(user_id) == 'waiting_for_inn':
        # Проверяем, является ли текст ИНН (обычно 10 или 12 цифр)
        if not text.isdigit():
            await update.effective_message.reply_text("ИНН должен содержать только цифры. Попробуйте снова.")
            return

        inn = text
        # Запрос к API ФНС
        try:
            search_url = 'https://egrul.nalog.ru/search'
            payload = {'query': inn}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.post(search_url, data=payload, headers=headers)
            search_results = response.json()

            if search_results.get('total') > 0:
                first_result_guid = search_results['rows'][0]['g']
                
                # Запрос деталей по GUID
                details_url = f'https://egrul.nalog.ru/get/{first_result_guid}'
                details_response = requests.get(details_url, headers=headers)
                details = details_response.json()

                full_name = details['result'][0].get('n', 'Наименование не найдено')
                await update.effective_message.reply_text(f"Найдено юридическое лицо:\n{full_name}")
            else:
                await update.effective_message.reply_text("Юридическое лицо с таким ИНН не найдено.")
        except Exception as e:
            logger.error(f"Ошибка при запросе к API ФНС: {e}")
            await update.effective_message.reply_text("Произошла ошибка при поиске по ИНН. Попробуйте позже или свяжитесь с нами.")

        # Сброс состояния после обработки
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