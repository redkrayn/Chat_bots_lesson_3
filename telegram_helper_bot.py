from environs import Env
from utils import detect_intent_texts, setup_logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def start(update, context):
    user = update.message.from_user
    update.message.reply_text(f'Здравствуйте, {user.first_name}!')


def handle_user_message(update, context):
    user_text = update.message.text
    chat_id = update.message.chat.id

    query_result = detect_intent_texts(
        project_id='verb-helper',
        session_id=f'tg-{chat_id}',
        texts=[user_text],
        language_code="ru"
    )

    response_text = query_result.fulfillment_text
    update.message.reply_text(response_text)


def main():
    env = Env()
    env.read_env()

    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')

    updater = Updater(telegram_bot_token)
    dp = updater.dispatcher

    logger_name = 'tg_verb_bot'
    logger = setup_logging(logger_name, updater.bot, telegram_chat_id)
    try:
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_message))

        logger.info('Бот запущен')

        updater.start_polling()
        updater.idle()

    except Exception as e:
        logger.error(f"Бот упал с ошибкой: {e}", exc_info=True)


if __name__ == '__main__':
    main()

