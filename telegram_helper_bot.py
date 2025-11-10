import logging

from environs import Env
from google.cloud import dialogflow
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def setup_logging(tg_bot=None, chat_id=None):
    logger = logging.getLogger('tg_verb_bot')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(message)s'
    )

    tg_handler = TelegramLogsHandler(tg_bot, chat_id)
    tg_handler.setLevel(logging.INFO)
    tg_handler.setFormatter(formatter)
    logger.addHandler(tg_handler)

    return logger


def start(update, context):
    user = update.message.from_user
    update.message.reply_text(f'Здравствуйте, {user.first_name}!')


def detect_intent_texts(project_id, session_id, texts, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

    return response.query_result.fulfillment_text


def echo(update, context):
    logger = context.bot_data['logger']
    try:
        user_text = update.message.text
        chat_id = update.message.chat.id

        response_text = detect_intent_texts(
            project_id='verb-helper',
            session_id=str(chat_id),
            texts=[user_text],
            language_code="ru"
        )

        update.message.reply_text(response_text)

    except Exception as e:
        logger.error(f"Бот упал с ошибкой: {e}", exc_info=True)


def main():
    env = Env()
    env.read_env()

    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')

    updater = Updater(telegram_bot_token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    logger = setup_logging(updater.bot, telegram_chat_id)
    updater.dispatcher.bot_data['logger'] = logger

    logger.info('Бот запущен')

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

