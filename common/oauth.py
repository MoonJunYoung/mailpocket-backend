import json
import os

import requests
from dotenv import load_dotenv

from backend.common.exceptions import InvalidOauthException

load_dotenv()
kakao_cilent_id = os.environ.get("KAKAO_CLIENT_ID")
kakao_redirect_url = os.environ.get("KAKAO_REDIRECT_URL")
naver_client_id = os.environ.get("NAVER_CLIENT_ID")
naver_client_secret = os.environ.get("NAVER_CLIENT_SECRET")
naver_state = os.environ.get("NAVER_STATE")


class Oauth:
    def get_user_platform_id_by_google_oauth(token):
        google_user_data = json.loads(
            requests.get(
                f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}"
            ).text
        )
        platform_id = google_user_data.get("id")
        if platform_id:
            return platform_id
        else:
            raise InvalidOauthException

    def get_user_platform_id_by_kakao_oauth(token):
        def _get_user_access_token_by_kakao_oauth(token):
            data = {
                "grant_type": "authorization_code",
                "client_id": kakao_cilent_id,
                "redirect_uri": kakao_redirect_url,
                "code": token,
            }
            kakao_token_data = json.loads(
                requests.post(
                    url=f"https://kauth.kakao.com/oauth/token", data=data
                ).text
            )
            access_token = kakao_token_data.get("access_token")
            return access_token

        access_token = _get_user_access_token_by_kakao_oauth(token)
        headers = {"Authorization": f"Bearer {access_token}"}
        kakao_user_data = json.loads(
            requests.get(url="https://kapi.kakao.com/v2/user/me", headers=headers).text
        )
        platform_id = kakao_user_data.get("id")
        if platform_id:
            return platform_id
        else:
            raise InvalidOauthException

    def get_user_platform_id_by_naver_oauth(token):
        def _get_user_access_token_by_naver_oauth(token):
            naver_token_data = json.loads(
                requests.post(
                    url=f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={naver_client_id}&client_secret={naver_client_secret}&code={token}&state={naver_state}"
                ).text
            )
            access_token = naver_token_data.get("access_token")
            return access_token

        access_token = _get_user_access_token_by_naver_oauth(token)
        headers = {"Authorization": f"Bearer {access_token}"}
        naver_user_data = json.loads(
            requests.get(
                url="https://openapi.naver.com/v1/nid/me", headers=headers
            ).text
        )
        platform_id = naver_user_data.get("response").get("id")
        if platform_id:
            return platform_id
        else:
            raise InvalidOauthException
