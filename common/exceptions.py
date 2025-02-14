import datetime
import logging
import traceback

from fastapi import HTTPException, Request

logging.basicConfig(filename="./backend_error.log", level=logging.ERROR)
logging.error(traceback.format_exc())


def catch_exception(exce, request: Request):
    date = datetime.datetime.now()
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0]
    else:
        client_ip = request.client.host
    request_path = request.url.path

    if issubclass(exce.__class__, CustomException):
        logging.error(
            f"\n===\ndate:{date}, ip:{client_ip}, request path:{request_path}\nA custom error occurred. : {exce}\n==="
        )
        print(
            f"\n===\ndate:{date}, ip:{client_ip}, request path:{request_path}\nA custom error occurred. : {exce}\n==="
        )
        raise HTTPException(status_code=exce.status_code, detail=exce.detail)
    logging.error(
        f"\n===\ndate:{date}, ip:{client_ip}, request path:{request_path}\nAn unexpected error occurred. : {exce}\ndetail : {traceback.format_exc()}==="
    )
    print(
        f"\n===\ndate:{date}, ip:{client_ip}, request path:{request_path}\nAn unexpected error occurred. : {exce}\ndetail : {traceback.format_exc()}==="
    )
    raise HTTPException(
        status_code=500,
        detail="An internal server error occurred. If the problem persists, please contact our support team.",
    )


class CustomException(Exception):
    status_code = ""
    detail = ""


class IdentifierAlreadyException(CustomException):
    def __init__(self, identifier) -> None:
        super().__init__(f"sign-up {identifier} this idnetifier is already")

    status_code = 409
    detail = "this idnetifier is already."


class TokenIsMissingException(CustomException):
    def __init__(self) -> None:
        super().__init__(f"authorization token is missing.")

    status_code = 401
    detail = "authorization token is missing."


class InvalidTokenException(CustomException):
    def __init__(self) -> None:
        super().__init__(f"invalid authorization token.")

    status_code = 401
    detail = "invalid authorization token."


class PasswordNotMatchException(CustomException):
    def __init__(self, identifier, password) -> None:
        super().__init__(
            f"sign-in password({password}) is not match to identifier({identifier})."
        )

    status_code = 401
    detail = "incorrect identifier or password."


class IdentifierNotFoundException(CustomException):
    def __init__(self, identifier) -> None:
        super().__init__(f"sign-in identifier({identifier}) is not found.")

    status_code = 401
    detail = "incorrect identifier or password."


class UnknownFromEamilException(CustomException):
    def __init__(self, from_email) -> None:
        super().__init__(f"{from_email} is unknown.")

    status_code = 401
    detail = "unknown from email"


class ChannelUserMismatchException(CustomException):
    def __init__(self, channel_id, user_id) -> None:
        super().__init__(f"this user:{user_id} does not own the channel:{channel_id}.")

    status_code = 401
    detail = "this user does not own the channel"


class InvalidOauthException(CustomException):
    def __init__(self) -> None:
        super().__init__(f"invalid Oatun Information")

    status_code = 401
    detail = "invalid Oatun Information"


class AlreadySubscribedException(CustomException):
    def __init__(self) -> None:
        super().__init__(f"You are already subscribed to that newsletter")

    status_code = 409
    detail = "You are already subscribed to that newsletter"


class NotSubscribedNewsletterException(CustomException):
    def __init__(self) -> None:
        super().__init__(
            f"You cannot unsubscribe from newsletters you are not subscribed to."
        )

    status_code = 409
    detail = "You cannot unsubscribe from newsletters you are not subscribed to."
