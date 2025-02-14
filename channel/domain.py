from backend.common.exceptions import ChannelUserMismatchException


class Channel:
    def __init__(
        self,
        id=None,
        webhook_url=None,
        slack_channel_id=None,
        team_name=None,
        team_icon=None,
        name=None,
        user_id=None,
    ) -> None:
        self.id = id
        self.webhook_url = webhook_url
        self.slack_channel_id = slack_channel_id
        self.team_name = team_name
        self.team_icon = team_icon
        self.name = name
        self.user_id = user_id

    def is_user_of_channel(self, user_id):
        if not self.user_id == user_id:
            raise ChannelUserMismatchException(self.id, user_id)
