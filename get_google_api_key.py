from environs import Env
from google.cloud import api_keys_v2
from google.cloud.api_keys_v2 import Key
from google.auth import load_credentials_from_file


def create_api_key(project_id: str, suffix: str, google_application_credentials) -> Key:
    credentials, project = load_credentials_from_file(google_application_credentials)

    client = api_keys_v2.ApiKeysClient(credentials=credentials)

    key = api_keys_v2.Key()
    key.display_name = f"My first API key - {suffix}"

    request = api_keys_v2.CreateKeyRequest()
    request.parent = f"projects/{project_id}/locations/global"
    request.key = key

    response = client.create_key(request=request).result()

    return response


if __name__ == '__main__':
    env = Env()
    env.read_env()
    google_application_credentials = env('GOOGLE_APPLICATION_CREDENTIALS')
    api_key = create_api_key('verb-helper', 'Verb Helper API Key', google_application_credentials)
    print(f"Successfully created an API key: {api_key.name}")
