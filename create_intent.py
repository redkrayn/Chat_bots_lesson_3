import json

import requests
from environs import Env
from google.cloud import dialogflow
from google.auth import load_credentials_from_file


def load_intents(credentials, intents_url):
    if intents_url.startswith(('http://', 'https://')):
        response = requests.get(intents_url)
        response.raise_for_status()
        phrases = response.json()
    else:
        with open(intents_url, 'r', encoding='utf-8') as file:
            phrases = json.load(file)

    created_intents = []

    for intent_name, intent_data in phrases.items():
        intent_response = create_intent(
            project_id='verb-helper',
            display_name=intent_name,
            training_phrases_parts=intent_data['questions'],
            message_texts=[intent_data['answer']],
            credentials=credentials
        )
        created_intents.append((intent_name, intent_response))

    return created_intents


def create_intent(project_id, display_name, training_phrases_parts, message_texts, credentials):
    credentials, project = load_credentials_from_file(credentials)
    intents_client = dialogflow.IntentsClient(credentials=credentials)

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []

    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    return response


if __name__ == '__main__':
    env = Env()
    env.read_env()
    google_application_credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    intents_url = env(
        'INTENTS_URL',
        'https://dvmn.org/media/filer_public/a7/db/a7db66c0-1259-4dac-9726-2d1fa9c44f20/questions.json'
    )

    created_intents = load_intents(google_application_credentials, intents_url)
    for intent_name, response in created_intents:
        print(f"Intent created: {intent_name} -> {response.name}")

