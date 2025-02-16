from fastapi import APIRouter, Header, Request
from pydantic import BaseModel

from common.exceptions import catch_exception
from common.oauth import Oauth
from common.token import Token
from user.service import UserService

user_service = UserService()


class LogInData(BaseModel):
    identifier: str
    password: str


class OauthData(BaseModel):
    token: str


class UserPresentation:
    router = APIRouter(prefix="/user")

    @router.get("", status_code=200)
    async def read(request: Request, Authorization: str = Header(None)):
        try:
            user_id = Token.get_user_id_by_token(Authorization)
            return user_service.read(user_id)

        except Exception as e:
            catch_exception(e, request)

    @router.post("", status_code=201)
    async def create_non_member_user(request: Request):
        try:
            user = user_service.create_non_member_user()
            return Token.create_token_by_user(user)
        except Exception as e:
            catch_exception(e, request)

    @router.post("/sign-up", status_code=201)
    async def sign_up(
        request: Request, login_data: LogInData, Authorization: str = Header(None)
    ):
        try:
            if Authorization:
                user_id = Token.get_user_id_by_token(Authorization)
                user = user_service.upgrade_non_meber_user_to_member(
                    user_id=user_id,
                    identifier=login_data.identifier,
                    password=login_data.password,
                )
            else:
                user = user_service.sign_up(
                    identifier=login_data.identifier,
                    password=login_data.password,
                )
            return Token.create_token_by_user(user)

        except Exception as e:
            catch_exception(e, request)

    @router.post("/sign-in", status_code=201)
    async def sign_in(request: Request, login_data: LogInData):
        try:
            user = user_service.sign_in(
                identifier=login_data.identifier,
                password=login_data.password,
            )
            return Token.create_token_by_user(user)
        except Exception as e:
            catch_exception(e, request)

    @router.post("/google-login", status_code=201)
    async def google_login(
        request: Request, oauth: OauthData, Authorization: str = Header(None)
    ):

        try:
            platform = "google"
            platform_id = Oauth.get_user_platform_id_by_google_oauth(oauth.token)
            if Authorization:
                user_id = Token.get_user_id_by_token(Authorization)
                user = user_service.upgrade_non_meber_user_to_member(
                    user_id=user_id,
                    platform_id=platform_id,
                    platform=platform,
                )
            else:
                user = user_service.oauth_login(platform_id, platform)

            return Token.create_token_by_user(user)

        except Exception as e:
            catch_exception(e, request)

    @router.post("/kakao-login", status_code=201)
    async def kakao_login(
        request: Request, oauth: OauthData, Authorization: str = Header(None)
    ):
        try:
            platform = "kakao"
            platform_id = Oauth.get_user_platform_id_by_kakao_oauth(oauth.token)
            if Authorization:
                user_id = Token.get_user_id_by_token(Authorization)
                user = user_service.upgrade_non_meber_user_to_member(
                    user_id=user_id,
                    platform_id=platform_id,
                    platform=platform,
                )
            else:
                user = user_service.oauth_login(platform_id, platform)
            return Token.create_token_by_user(user)

        except Exception as e:
            catch_exception(e, request)

    @router.post("/naver-login", status_code=201)
    async def naver_login(
        request: Request, oauth: OauthData, Authorization: str = Header(None)
    ):
        try:
            platform = "naver"
            platform_id = Oauth.get_user_platform_id_by_naver_oauth(oauth.token)
            if Authorization:
                user_id = Token.get_user_id_by_token(Authorization)
                user = user_service.upgrade_non_meber_user_to_member(
                    user_id=user_id,
                    platform_id=platform_id,
                    platform=platform,
                )
            else:
                user = user_service.oauth_login(platform_id, platform)
            return Token.create_token_by_user(user)

        except Exception as e:
            catch_exception(e, request)
