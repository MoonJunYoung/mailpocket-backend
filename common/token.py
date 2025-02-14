import datetime
import os

import jwt
from dotenv import load_dotenv

from backend.common.exceptions import InvalidTokenException, TokenIsMissingException
from backend.user.domain import User

load_dotenv()
secret_key = os.environ.get("JWT_SECRET_KEY")


class Token:
    def create_token_by_user(user: User):
        payload = {
            "id": user.id,
            "is_member": user.is_member,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
        }
        token = jwt.encode(payload, secret_key)
        return token

    def get_user_id_by_token(token):
        if not token:
            raise TokenIsMissingException
        try:
            token_info = jwt.decode(token, secret_key, algorithms="HS256")
        except jwt.exceptions.DecodeError:
            raise InvalidTokenException
        token_user_id = token_info.get("id")
        return token_user_id
