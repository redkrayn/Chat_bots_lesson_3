import logging

from google.cloud import dialogflow


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def setup_logging(logger_name, tg_bot=None, chat_id=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(message)s'
    )

    tg_handler = TelegramLogsHandler(tg_bot, chat_id)
    tg_handler.setLevel(logging.INFO)
    tg_handler.setFormatter(formatter)
    logger.addHandler(tg_handler)

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

