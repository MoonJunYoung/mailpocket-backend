from fastapi import APIRouter, Header, Request, Response
from pydantic import BaseModel

from channel.service import ChannelService
from common.exceptions import catch_exception
from common.token import Token

channel_service = ChannelService()


class SlackOauthData(BaseModel):
    code: str


class ChannelPresentation:
    router = APIRouter(prefix="/channel")

    @router.get("", status_code=200)
    async def read_channels(request: Request, Authorization=Header(None)):
        try:
            user_id = Token.get_user_id_by_token(Authorization)
            channels = channel_service.get_channels(user_id)
            return channels

        except Exception as e:
            catch_exception(e, request)

    @router.post("", status_code=201)
    async def add_channel(
        request: Request,
        response: Response,
        slack_oauth_data: SlackOauthData,
        Authorization=Header(None),
    ):
        try:
            user_id = Token.get_user_id_by_token(Authorization)
            channel_id = channel_service.add_channel(slack_oauth_data.code, user_id)
            response.headers["Location"] = f"channel/{channel_id}"
        except Exception as e:
            catch_exception(e, request)

    @router.get("/{channel_id}", status_code=200)
    async def read_channel(
        request: Request,
        channel_id: int,
        Authorization=Header(None),
    ):
        try:
            user_id = Token.get_user_id_by_token(Authorization)
            channel = channel_service.get_channel(user_id, channel_id)
            return channel
        except Exception as e:
            catch_exception(e, request)

    @router.delete("/{channel_id}", status_code=204)
    async def delete_channel(
        request: Request,
        channel_id: int,
        Authorization=Header(None),
    ):
        try:
            user_id = Token.get_user_id_by_token(Authorization)
            channel_service.remove_channel(user_id, channel_id)

        except Exception as e:
            catch_exception(e, request)
