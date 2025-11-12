import random
import telegram
import vk_api as vk

from environs import Env
from utils import detect_intent_texts, setup_logging, create_session_id
from vk_api.longpoll import VkLongPoll, VkEventType


def handle_user_message(event, vk_api):
    session_id = create_session_id("vk", event.user_id)

    dialogflow_response = detect_intent_texts(
        project_id='verb-helper',
        session_id=session_id,
        texts=[event.text],
        language_code='ru'
    )

    if not dialogflow_response.intent.is_fallback:
        vk_api.messages.send(
            user_id=event.user_id,
            message=dialogflow_response.fulfillment_text,
            random_id=random.randint(1, 1000)
        )


def main():
    env = Env()
    env.read_env()

    vk_token = env('VK_TOKEN')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')
    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')

    tg_bot = telegram.Bot(token=telegram_bot_token)

    logger_name = 'vk_verb_bot'
    logger = setup_logging(logger_name, tg_bot, telegram_chat_id)

    try:
        vk_session = vk.VkApi(token=vk_token)
        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)

        logger.info('Бот запущен')

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                handle_user_message(event, vk_api)

    except Exception as e:
        logger.error(f"Бот упал с ошибкой: {e}", exc_info=True)


if __name__ == "__main__":
    main()

