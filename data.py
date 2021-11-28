import os
import requests
import zipfile


def download_file_from_google_drive(id_, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id_}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id_, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def get_data():
    id_ = os.environ.get('GDRIVE_DATA_ID')

    if id_ is None:
        raise ValueError('"GDRIVE_DATA_ID" environment variable is not set!')

    download_file_from_google_drive(id_, 'beer_data.zip')

    with zipfile.ZipFile('beer_data.zip', 'r') as zip_:
        zip_.extractall()

    os.remove('beer_data.zip')
