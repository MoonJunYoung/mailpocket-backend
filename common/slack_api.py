import json
import os

import requests
from dotenv import load_dotenv

from channel.domain import Channel
from mail.domain import Mail
from newsletter.domain import NewsLetter

load_dotenv()
client_id = os.environ.get("SLACK_CLIENT_ID")
client_secret = os.environ.get("SLACK_CLIENT_SECRET")
slack_logging_channel_webhook_url = os.environ.get("SLACK_LOGGING_CHANNEL_WEBHOOK_URL")

slack_logging_unknown_email_address_webhook_url = os.environ.get(
    "SLACK_UNKNOWN_EMAIL_ADDRESS_WEBHOOK_URL"
)


class SlackAPI:
    def connect_workspace(self, code, user_id):
        url = "https://slack.com/api/oauth.v2.access"
        data = {"client_id": client_id, "client_secret": client_secret, "code": code}
        response_json = requests.post(url, data=data).json()
        access_token = response_json.get("access_token")
        webhook_url = response_json.get("incoming_webhook").get("url").replace("\\", "")
        slack_channel_id = response_json.get("incoming_webhook").get("channel_id")
        name = response_json.get("incoming_webhook").get("channel")
        team_name = response_json.get("team").get("name")
        team_icon = self._get_team_icon(access_token)
        channel = Channel(
            id=None,
            webhook_url=webhook_url,
            slack_channel_id=slack_channel_id,
            team_name=team_name,
            team_icon=team_icon,
            name=name,
            user_id=user_id,
        )
        return channel

    def _get_team_icon(self, access_token):
        url = "https://slack.com/api/team.info"
        response = requests.get(
            url, headers={"Authorization": f"Bearer {access_token}"}
        )
        team_icon = (
            response.json().get("team").get("icon").get("image_230").replace("\\", "")
        )
        return team_icon

    def loging(
        self,
        mail: Mail,
    ):
        notification_text = self.__make_log_notification_text(mail)
        data = {"blocks": notification_text}
        resp = requests.post(
            url=slack_logging_channel_webhook_url,
            data=json.dumps(data),
        )

        print("log notification", resp.text)

    def __make_log_notification_text(self, mail: Mail):
        notification_text = [
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"email : {mail.from_email}\nid : {mail.from_name}\n*<{mail.read_link}|{mail.subject}>*",
                    }
                ],
            },
        ]

        return notification_text

    def sending_welcome_message(self, channel: Channel):
        welcome_message = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "이제부터 이 채널에 뉴스레터를 요약해서 보내드릴게요.\n메일 포켓을 사용하면 이런 게 좋아요.\n\n*1) 매일 쏟아지는 뉴스레터를 3줄 요약해서 슬랙에 보내드려요.*\n눈으로만 훑어보세요. 재미 있는 뉴스라면 조금 더 자세히 보고, 슬랙의 save item 을 사용하면 나중에 읽을 수도 있어요.\n*2) 메일함에 일회성 메일이 쌓이는걸 방지할 수 있어요.*\n뉴스레터 때문에 메일함이 항상 999+ 개 이상 쌓여 있고, 중요 메일 놓쳐본 적 많으시죠? 뉴스레터는 메일 포켓이 받고, 슬랙으로 요약해서 슝- 보내 드릴게요.",
                },
            }
        ]
        data = {"blocks": welcome_message}
        requests.post(url=channel.webhook_url, data=json.dumps(data))

    def sending_mail_recv_notification(
        self, channel: Channel, mail: Mail, newsletter: NewsLetter
    ):
        notification_text = self.__make_notification_text(channel, mail, newsletter)
        data = {"blocks": notification_text}
        resp = requests.post(url=channel.webhook_url, data=json.dumps(data))
        print("notification", resp.text)

    def __make_notification_text(
        self, channel: Channel, mail: Mail, newsletter: NewsLetter
    ):
        utm_source = (
            f"&utm_source=slack&utm_medium=bot&utm_campaign={channel.team_name}"
        )
        notification_text = [
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"{newsletter.name}의 새로운 소식이 도착했어요.\n*<{mail.read_link}{utm_source}|{mail.subject}>*",
                    }
                ],
            },
        ]
        if mail.summary_list:
            summary_news_slack_notification_text_list = list()
            for subject, content in mail.summary_list.items():
                summary_news_slack_notification_text_list.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{subject}*\n{content}",
                        },
                    }
                )
            notification_text += summary_news_slack_notification_text_list
        return notification_text

    def loging_unknown_email_address(
        self,
        mail: Mail,
    ):
        mrkdwn_text = f"{mail.from_email}\nis unknown email address\n뉴스레터: {mail.from_name}\n제목: {mail.subject}\n링크: {mail.read_link}\nS3 OBJ KEY: {mail.s3_object_key}"
        data = self.__make_one_slack_message_blocks(mrkdwn_text)

        requests.post(
            url=slack_logging_unknown_email_address_webhook_url,
            data=data,
        )

    def __make_one_slack_message_blocks(self, mrkdwn_text):
        slack_message_block = {
            "blocks": [
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": mrkdwn_text,
                        }
                    ],
                },
            ]
        }
        data = json.dumps(slack_message_block)
        return data
