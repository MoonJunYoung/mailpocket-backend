import os

import requests
from dotenv import load_dotenv

from user.domain import User

load_dotenv()

client_key = os.environ.get("AMPLITUDE_CLIENT_KEY")


def get_experiment(user: User):
    user_id = user.id
    if user.platform:
        user_id = f"{user.platform}_{user.id}"
    elif user.identifier:
        user_id = user.identifier

    headers = {"Authorization": f"Api-Key {client_key}"}
    resp = requests.get(
        url=f"https://api.lab.amplitude.com/v1/vardata?user_id={user_id}",
        headers=headers,
    )
    return resp.json()
