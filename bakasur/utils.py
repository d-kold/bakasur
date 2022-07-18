import os
import json
from bakasur.constants import (THUISBEZORGD_TOKEN_FILE,
                               DB_FILEPATH,
                               HEADERS)


def token_file_exists():
    """
    Checks whether the token file is present or not
    """
    return os.path.exists(os.path.join(THUISBEZORGD_TOKEN_FILE))


def db_file_exists():
    """
    Checks whether the DB file is present or not
    """
    return os.path.exists(os.path.join(DB_FILEPATH))


def get_headers():
    """
    Adds the authorization token to the headers
    """
    with open(THUISBEZORGD_TOKEN_FILE, 'r') as token_file:
        f = json.load(token_file)
        auth_token = f['authToken']
    headers = HEADERS.copy()
    headers['authorization'] = 'Bearer ' + auth_token
    return headers


def get_tokens():
    """
    Return json data for refresh tokens request
    """
    with open(THUISBEZORGD_TOKEN_FILE, 'r') as token_file:
        tokens = json.load(token_file)
    return {
        'accessToken': tokens.get('authToken'),
        'refreshToken': tokens.get('refreshToken'),
    }


def update_token_file(data):
    """
    Write the newly received tokens to the token for future use
    """
    # print("Writing file")
    with open(THUISBEZORGD_TOKEN_FILE, 'w') as outfile:
        json.dump(data, outfile)
