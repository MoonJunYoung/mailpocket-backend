from channel.domain import Channel
from channel.repository import ChannelRepository
from common.slack_api import SlackAPI
from mail.domain import Mail
from mail.repository import MailRepository
from newsletter.domain import NewsLetter
from newsletter.repository import NewsLetterRepository
from user.domain import User
from user.repository import UserRepository


class ChannelDTO:
    def __init__(self, channel: Channel) -> None:
        self.id = channel.id
        self.team_name = channel.team_name
        self.team_icon = channel.team_icon
        self.name = channel.name


class ChannelService:
    def __init__(self) -> None:
        self.mail_repository = MailRepository()
        self.user_repository = UserRepository()
        self.channel_repository = ChannelRepository()
        self.newsletter_repository = NewsLetterRepository()
        self.slack_api = SlackAPI()

    def add_channel(self, code, user_id):
        user = self.user_repository.ReadByID(user_id)
        channel = self.slack_api.connect_workspace(code, user_id)
        self.channel_repository.Create(channel).run()
        if channel.id:
            self.slack_api.sending_welcome_message(channel=channel)
            subscribed_newsletter_list = (
                self.newsletter_repository.ReadFilteredNewsletters(
                    user=user,
                    subscribe_status="subscribed",
                    sort_type="recent",
                    in_mail=True,
                    cursor=None,
                    category_id=None,
                    size=3,
                ).run()
            )
            for subscribed_newsletter in subscribed_newsletter_list:
                self.mail_repository.load_mail_data_by_s3_object_key(
                    subscribed_newsletter.mail
                )
                self.slack_api.sending_mail_recv_notification(
                    channel=channel,
                    mail=subscribed_newsletter.mail,
                    newsletter=subscribed_newsletter,
                )

            return channel.id

    def get_channels(self, user_id):
        channel_list = list()
        channels = self.channel_repository.ReadChannelsByUserID(user_id).run()
        for channel in channels:
            channel_list.append(ChannelDTO(channel))
        return channel_list

    def get_channel(self, user_id, channel_id):
        channel = self.channel_repository.ReadChannelByID(channel_id).run()
        return ChannelDTO(channel)

    def remove_channel(self, user_id, channel_id):
        channel = self.channel_repository.ReadChannelByID(channel_id).run()
        channel.is_user_of_channel(user_id)
        self.channel_repository.Delete(channel).run()
