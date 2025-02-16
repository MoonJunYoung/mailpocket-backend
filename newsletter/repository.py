import datetime

from sqlalchemy import func

from common.database.connector import MysqlCRUDTemplate
from common.database.model import (
    CategoryModel,
    MailModel,
    NewsletterEmailAddressesModel,
    NewsLetterModel,
    SubscribeModel,
    SubscribeRankingModel,
)
from common.exceptions import UnknownFromEamilException
from mail.domain import Mail
from newsletter.domain import Category, NewsLetter
from user.domain import User


class NewsLetterRepository:
    class LoadNewsLetterByFromEmail(MysqlCRUDTemplate):
        def __init__(self, from_email) -> None:
            self.from_email = from_email
            super().__init__()

        def execute(self):
            newsletter_model = (
                self.session.query(NewsLetterModel)
                .join(
                    NewsletterEmailAddressesModel,
                    NewsLetterModel.id == NewsletterEmailAddressesModel.newsletter_id,
                )
                .filter(NewsletterEmailAddressesModel.email_address == self.from_email)
                .first()
            )
            if not newsletter_model:
                return False
            newsletter = NewsLetter(
                id=newsletter_model.id,
                name=newsletter_model.name,
                category_id=newsletter_model.category_id,
                send_date=newsletter_model.send_date,
            )
            return newsletter

        def run(self) -> NewsLetter:
            return super().run()

    class LoadNewsLetterByIDWithMails(MysqlCRUDTemplate):
        def __init__(self, id) -> None:
            self.id = id
            super().__init__()

        def execute(self):
            newsletter_model = (
                self.session.query(NewsLetterModel)
                .filter(NewsLetterModel.id == self.id)
                .first()
            )
            if not newsletter_model:
                return None
            mail_list = list()
            mail_models = (
                self.session.query(MailModel)
                .filter(MailModel.newsletter_id == newsletter_model.id)
                .order_by(MailModel.recv_at.desc())
                .all()
            )
            for mail_model in mail_models:
                mail = Mail(
                    id=mail_model.id,
                    s3_object_key=mail_model.s3_object_key,
                    subject=mail_model.subject,
                    recv_at=mail_model.recv_at,
                )
                mail_list.append(mail)
            newsletter = NewsLetter(
                id=newsletter_model.id,
                name=newsletter_model.name,
                category_id=newsletter_model.category_id,
                send_date=newsletter_model.send_date,
                mails=mail_list,
            )
            return newsletter

    class ReadAllNewsletters(MysqlCRUDTemplate):
        def execute(self):
            newsletter_list = list()
            newsletter_models = self.session.query(NewsLetterModel).all()
            for newsletter_model in newsletter_models:
                newsletter_list.append(
                    NewsLetter(
                        id=newsletter_model.id,
                        name=newsletter_model.name,
                        category_id=newsletter_model.category_id,
                        send_date=newsletter_model.send_date,
                        operating_status=newsletter_model.operating_status,
                    )
                )
            return newsletter_list

    class ReadFilteredNewsletters(MysqlCRUDTemplate):
        def __init__(
            self,
            user: User,
            subscribe_status,
            sort_type,
            in_mail,
            cursor,
            category_id,
            size=None,
        ) -> None:
            super().__init__()
            self.user = user
            self.newsletter_list = list()
            if sort_type == "recent":
                self.table_model = self.session.query(NewsLetterModel).order_by(
                    NewsLetterModel.last_recv_at.desc()
                )
            elif sort_type == "ranking":
                if not self.__check_if_subscribe_ranking_is_today():
                    self.__update_subscribe_ranking()

                self.table_model = (
                    self.session.query(NewsLetterModel)
                    .join(
                        SubscribeRankingModel,
                        NewsLetterModel.id == SubscribeRankingModel.newsletter_id,
                    )
                    .order_by(SubscribeRankingModel.id)
                )
            if category_id:
                self.table_model = self.table_model.filter(
                    NewsLetterModel.category_id == category_id
                )
            subscribe_models = (
                self.session.query(SubscribeModel.newsletter_id)
                .filter(SubscribeModel.user_id == self.user.id)
                .all()
            )
            subscribed_newsletter_ids = [
                subscribe_model[0] for subscribe_model in subscribe_models
            ]

            if subscribe_status == "subscribed":
                self.newsletter_models = self.table_model.filter(
                    NewsLetterModel.id.in_(subscribed_newsletter_ids)
                )
            elif subscribe_status == "subscribable":
                self.newsletter_models = self.table_model.filter(
                    NewsLetterModel.id.not_in(subscribed_newsletter_ids)
                )

            if in_mail and not cursor and subscribe_status == "subscribable":
                self.newsletter_models = self.newsletter_models.limit(8)

            elif in_mail and cursor and subscribe_status == "subscribable":
                cursor_row = (
                    self.session.query(SubscribeRankingModel)
                    .filter(SubscribeRankingModel.newsletter_id == cursor)
                    .first()
                )
                self.newsletter_models = self.newsletter_models.filter(
                    SubscribeRankingModel.id > cursor_row.id
                ).limit(8)

            elif size:
                self.newsletter_models = self.newsletter_models.limit(size)

            else:
                self.newsletter_models = self.newsletter_models.all()

            for newsletter_model in self.newsletter_models:
                mail = None
                if in_mail:
                    mail_model = (
                        self.session.query(MailModel)
                        .filter(MailModel.newsletter_id == newsletter_model.id)
                        .order_by(MailModel.id.desc())
                        .first()
                    )
                    if mail_model:
                        mail = Mail(
                            id=mail_model.id,
                            s3_object_key=mail_model.s3_object_key,
                            subject=mail_model.subject,
                            summary_list=mail_model.summary_list,
                            newsletter_id=mail_model.newsletter_id,
                        )
                newsletter = NewsLetter(
                    id=newsletter_model.id,
                    name=newsletter_model.name,
                    category_id=newsletter_model.category_id,
                    send_date=newsletter_model.send_date,
                    mail=mail,
                )
                self.newsletter_list.append(newsletter)

        def execute(self):
            return self.newsletter_list

        def __check_if_subscribe_ranking_is_today(self):
            subscribe_ranking_model = self.session.query(SubscribeRankingModel).first()
            return subscribe_ranking_model.snapshot_at == datetime.date.today()

        def __update_subscribe_ranking(self):
            self.session.query(SubscribeRankingModel).delete()
            newsletter_models = (
                self.session.query(
                    NewsLetterModel.id,
                    func.count(SubscribeModel.newsletter_id),
                )
                .outerjoin(
                    SubscribeModel,
                    NewsLetterModel.id == SubscribeModel.newsletter_id,
                )
                .filter(NewsLetterModel.operating_status == True)
                .group_by(NewsLetterModel.id)
                .order_by(func.count(SubscribeModel.newsletter_id).desc())
                .all()
            )
            subscribe_ranking_models = [
                SubscribeRankingModel(newsletter_model[0], newsletter_model[1])
                for newsletter_model in newsletter_models
            ]
            self.session.add_all(subscribe_ranking_models)
            self.session.commit()

        def run(self) -> list[NewsLetter]:
            return super().run()

    class UpdateNewsletterLastRecvDateTime(MysqlCRUDTemplate):
        def __init__(self, newsletter: NewsLetter) -> None:
            self.newsletter = newsletter
            super().__init__()

        def execute(self):
            newsletter_model = (
                self.session.query(NewsLetterModel)
                .filter(NewsLetterModel.id == self.newsletter.id)
                .first()
            )
            newsletter_model.last_recv_at = datetime.datetime.now()
            self.session.commit()

    class ReadCategoriesOfNewsletter(MysqlCRUDTemplate):
        def execute(self):
            category_list = list()
            category_models = self.session.query(CategoryModel).all()
            for category_model in category_models:
                category_list.append(Category(category_model.id, category_model.name))
            return category_list
