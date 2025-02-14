import datetime

from sqlalchemy import DATE, DATETIME, JSON, Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "user"
    id = Column("id", Integer, primary_key=True)
    identifier = Column(String)
    password = Column(String)
    platform = Column(String)
    platform_id = Column(String)
    is_member = Column(Boolean)

    def __init__(self, id, identifier, password, platform, platform_id, is_member):
        self.id = id
        self.identifier = identifier
        self.password = password
        self.platform = platform
        self.platform_id = platform_id
        self.is_member = is_member


class ChannelModel(Base):
    __tablename__ = "channel"
    id = Column("id", Integer, primary_key=True)
    webhook_url = Column(String)
    slack_channel_id = Column(String)
    name = Column(String)
    team_name = Column(String)
    team_icon = Column(String)
    user_id = Column(Integer)

    def __init__(
        self, id, webhook_url, slack_channel_id, name, team_name, team_icon, user_id
    ):
        self.id = id
        self.webhook_url = webhook_url
        self.slack_channel_id = slack_channel_id
        self.name = name
        self.team_name = team_name
        self.team_icon = team_icon
        self.user_id = user_id


class NewsLetterModel(Base):
    __tablename__ = "newsletter"
    id = Column("id", Integer, primary_key=True)
    name = Column(String)
    from_email = Column(String)
    send_date = Column(String)
    last_recv_at = Column(DATETIME)
    operating_status = Column(Boolean)
    category_id = Column(Integer)

    def __init__(self, id, name, from_email, send_date, category_id=None):
        self.id = id
        self.name = name
        self.from_email = from_email
        self.send_date = send_date
        self.category_id = category_id


class NewsletterEmailAddressesModel(Base):
    __tablename__ = "newsletter_email_addresses"
    id = Column("id", Integer, primary_key=True)
    newsletter_id = Column(Integer)
    email_address = Column(String)

    def __init__(self, id, newsletter_id, email_address):
        self.id = id
        self.newsletter_id = newsletter_id
        self.email_address = email_address


class SubscribeModel(Base):
    __tablename__ = "subscribe"
    id = Column("id", Integer, primary_key=True)
    newsletter_id = Column(Integer)
    user_id = Column(Integer)

    def __init__(self, id, newsletter_id, user_id):
        self.id = id
        self.newsletter_id = newsletter_id
        self.user_id = user_id


class SubscribeRankingModel(Base):
    __tablename__ = "subscribe_ranking"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    newsletter_id = Column(Integer)
    subscribe_count = Column(Integer)
    snapshot_at = Column(DATE, default=datetime.date.today())

    def __init__(self, newsletter_id, subscribe_count):
        self.newsletter_id = newsletter_id
        self.subscribe_count = subscribe_count


class MailModel(Base):
    __tablename__ = "mail"
    id = Column("id", Integer, primary_key=True)
    s3_object_key = Column(String)
    subject = Column(String)
    summary_list = Column(JSON)
    newsletter_id = Column(Integer)

    recv_at = Column(DATETIME)

    def __init__(
        self, id, s3_object_key, subject, summary_list, newsletter_id, recv_at=None
    ):
        self.id = id
        self.s3_object_key = s3_object_key
        self.subject = subject
        self.summary_list = summary_list
        self.newsletter_id = newsletter_id
        self.recv_at = recv_at


class CategoryModel(Base):
    __tablename__ = "category"
    id = Column("id", Integer, primary_key=True)
    name = Column(String)

    def __init__(self, id, name):
        self.id = id
        self.name = name
