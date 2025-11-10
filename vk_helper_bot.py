import random
import logging
import telegram
import vk_api as vk

from environs import Env
from google.cloud import dialogflow
from vk_api.longpoll import VkLongPoll, VkEventType


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def setup_logging(tg_bot=None, chat_id=None):
    logger = logging.getLogger('vk_verb_bot')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(message)s'
    )

    telegram_handler = TelegramLogsHandler(tg_bot, chat_id)
    telegram_handler.setLevel(logging.INFO)
    telegram_handler.setFormatter(formatter)
    logger.addHandler(telegram_handler)

    return logger


def detect_intent_texts(project_id, session_id, texts, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

    return response.query_result


def echo(event, vk_api, logger):
    try:
        dialogflow_response = detect_intent_texts(
            project_id='verb-helper',
            session_id=str(event.user_id),
            texts=[event.text],
            language_code='ru'
        )

        if not dialogflow_response.intent.is_fallback:
            vk_api.messages.send(
                user_id=event.user_id,
                message=dialogflow_response.fulfillment_text,
                random_id=random.randint(1, 1000)
            )

    except Exception as e:
        logger.error(f"Бот упал с ошибкой: {e}", exc_info=True)


if __name__ == "__main__":
    env = Env()
    env.read_env()

    vk_token = env('VK_TOKEN')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')
    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    tg_bot = telegram.Bot(token=telegram_bot_token)

    logger = setup_logging(tg_bot, telegram_chat_id)
    logger.info('Бот запущен')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api, logger)
