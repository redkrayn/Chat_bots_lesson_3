from environs import Env
from google.cloud import dialogflow
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


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
    user_text = update.message.text
    chat_id = update.message.chat.id

    response_text = detect_intent_texts(
        project_id='verb-helper',
        session_id=str(chat_id),
        texts=[user_text],
        language_code="ru"
    )

    update.message.reply_text(response_text)


def main():
    env = Env()
    env.read_env()
    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')

    updater = Updater(telegram_bot_token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

