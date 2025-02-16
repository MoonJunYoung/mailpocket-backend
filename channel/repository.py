from channel.domain import Channel
from common.database.connector import MysqlCRUDTemplate
from common.database.model import ChannelModel, SubscribeModel
from common.exceptions import UnknownFromEamilException
from newsletter.domain import NewsLetter


class ChannelRepository:
    class ReadChannelsByUserID(MysqlCRUDTemplate):
        def __init__(self, user_id) -> None:
            self.user_id = user_id
            super().__init__()

        def execute(self):
            channels = list()
            channel_models = (
                self.session.query(ChannelModel)
                .filter(ChannelModel.user_id == self.user_id)
                .all()
            )
            if not channel_models:
                return channels
            for channel_model in channel_models:
                channel = Channel(
                    id=channel_model.id,
                    webhook_url=channel_model.webhook_url,
                    slack_channel_id=channel_model.slack_channel_id,
                    name=channel_model.name,
                    team_name=channel_model.team_name,
                    team_icon=channel_model.team_icon,
                    user_id=channel_model.user_id,
                )
                channels.append(channel)
            return channels

    class ReadChannelByID(MysqlCRUDTemplate):
        def __init__(self, id) -> None:
            self.id = id
            super().__init__()

        def execute(self):
            channel_model = (
                self.session.query(ChannelModel)
                .filter(ChannelModel.id == self.id)
                .first()
            )
            channel = Channel(
                id=channel_model.id,
                webhook_url=channel_model.webhook_url,
                slack_channel_id=channel_model.slack_channel_id,
                name=channel_model.name,
                team_name=channel_model.team_name,
                team_icon=channel_model.team_icon,
                user_id=channel_model.user_id,
            )
            return channel

        def run(self) -> Channel:
            return super().run()

    class Create(MysqlCRUDTemplate):
        def __init__(self, channel: Channel) -> None:
            self.channel = channel
            super().__init__()

        def execute(self):
            channel_model = ChannelModel(
                id=None,
                webhook_url=self.channel.webhook_url,
                slack_channel_id=self.channel.slack_channel_id,
                name=self.channel.name,
                team_name=self.channel.team_name,
                team_icon=self.channel.team_icon,
                user_id=self.channel.user_id,
            )
            self.session.add(channel_model)
            self.session.commit()
            self.channel.id = channel_model.id

    class ReadChannelsByNewsletter(MysqlCRUDTemplate):
        def __init__(self, newsletter: NewsLetter) -> None:
            self.newsletter = newsletter
            super().__init__()

        def execute(self):
            channels = list()
            subscribe_models = (
                self.session.query(SubscribeModel)
                .filter(SubscribeModel.newsletter_id == self.newsletter.id)
                .all()
            )
            if not subscribe_models:
                return None
            for subscribe_model in subscribe_models:
                user_id = subscribe_model.user_id
                channel_models = (
                    self.session.query(ChannelModel)
                    .filter(ChannelModel.user_id == user_id)
                    .all()
                )
                for channel_model in channel_models:
                    channel = Channel(
                        id=channel_model.id,
                        webhook_url=channel_model.webhook_url,
                        slack_channel_id=channel_model.slack_channel_id,
                        name=channel_model.name,
                        team_name=channel_model.team_name,
                        team_icon=channel_model.team_icon,
                        user_id=channel_model.user_id,
                    )
                    channels.append(channel)
            return channels

        def run(self) -> list[Channel]:
            return super().run()

    class Delete(MysqlCRUDTemplate):
        def __init__(self, channel: Channel) -> None:
            self.channel = channel
            super().__init__()

        def execute(self):
            channel_model = (
                self.session.query(ChannelModel)
                .filter(ChannelModel.id == self.channel.id)
                .first()
            )
            self.session.delete(channel_model)
            self.session.commit()
