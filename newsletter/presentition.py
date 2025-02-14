from enum import Enum

from fastapi import APIRouter, Header, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.common.exceptions import catch_exception
from backend.common.token import Token
from backend.mail.service import MailService
from backend.newsletter.service import NewsLetterService

newsletter_service = NewsLetterService()
mail_service = MailService()


class SubscribeData(BaseModel):
    ids: list[int]


class SubscribeStatus(str, Enum):
    subscribed = "subscribed"
    subscribable = "subscribable"


class SortType(str, Enum):
    ranking = "ranking"
    recent = "recent"


class NewsLetterPresentation:
    router = APIRouter(prefix="/newsletter")

    @router.get("", status_code=200)
    async def get_newsletters(
        request: Request,
        subscribe_status: SubscribeStatus,
        sort_type: SortType,
        in_mail: bool = False,
        cursor: int = None,
        category_id: int = None,
        Authorization=Header(None),
    ):
        try:
            user_id = Token.get_user_id_by_token(Authorization)
            newsletters = newsletter_service.get_newsletters(
                user_id, subscribe_status, sort_type, in_mail, cursor, category_id
            )
            return newsletters
        except Exception as e:
            catch_exception(e, request)

    @router.put("/subscribe", status_code=201)
    async def newsletters_subscribe(
        request: Request,
        subscribe_data: SubscribeData,
        Authorization=Header(None),
    ):
        try:
            user_id = Token.get_user_id_by_token(Authorization)
            newsletter_service.newsletters_subscribe(user_id, subscribe_data.ids)

        except Exception as e:
            catch_exception(e, request)

    @router.post("/{newsletter_id}/subscribe", status_code=201)
    async def newsletter_subscribe(
        request: Request,
        newsletter_id: int,
        Authorization=Header(None),
    ):
        try:
            user_id = Token.get_user_id_by_token(Authorization)
            newsletter_service.newsletter_subscribe(user_id, newsletter_id)

        except Exception as e:
            catch_exception(e, request)

    @router.delete("/{newsletter_id}/subscribe", status_code=204)
    async def newsletter_subscribe_cancel(
        request: Request,
        newsletter_id: int,
        Authorization=Header(None),
    ):
        try:
            user_id = Token.get_user_id_by_token(Authorization)
            newsletter_service.newsletter_subscribe_cancel(user_id, newsletter_id)

        except Exception as e:
            catch_exception(e, request)

    @router.get("/{newsletter_id}/mail", status_code=200)
    async def get_newsletter_with_previous_mail_list(
        request: Request,
        newsletter_id: int,
        Authorization=Header(None),
    ):
        try:
            Token.get_user_id_by_token(Authorization)
            newsltter = newsletter_service.get_newsletter_with_previous_mail_list_by_newsletter_id(
                newsletter_id
            )
            return newsltter
        except Exception as e:
            catch_exception(e, request)

    @router.get("/{newsletter_id}/last-mail", status_code=200)
    async def get_newsletter_with_last_mail(
        request: Request,
        newsletter_id: int,
        Authorization=Header(None),
    ):
        try:
            Token.get_user_id_by_token(Authorization)
            mail = mail_service.get_last_mail_of_newsletter_by_newsletter_id(
                newsletter_id
            )
            return mail
        except Exception as e:
            catch_exception(e, request)

    @router.get("/categories", status_code=200)
    async def get_category_list(
        request: Request,
    ):
        try:
            category_list = newsletter_service.get_category_list()
            return category_list
        except Exception as e:
            catch_exception(e, request)
