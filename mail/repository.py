from backend.common.database.connector import MysqlCRUDTemplate
from backend.common.database.model import MailModel
from backend.common.s3 import S3Connector
from backend.mail.domain import Mail
from backend.newsletter.domain import NewsLetter


class MailRepository(S3Connector):
    def read_mail_data_by_s3_object_key(self, s3_object_key):
        try:
            object = self.seoul_s3_client.get_object(
                Bucket=self.seoul_bucket_name, Key=s3_object_key
            )
        except:
            object = self.virginia_s3_client.get_object(
                Bucket=self.virginia_bucket_name, Key=s3_object_key
            )
        mail_content = object["Body"].read()
        mail = Mail(id=None, mail_content=mail_content, s3_object_key=s3_object_key)
        return mail

    def load_mail_data_by_s3_object_key(self, mail: Mail):
        try:
            object = self.seoul_s3_client.get_object(
                Bucket=self.seoul_bucket_name, Key=mail.s3_object_key
            )
        except:
            object = self.virginia_s3_client.get_object(
                Bucket=self.virginia_bucket_name, Key=mail.s3_object_key
            )
        mail_content = object["Body"].read()
        mail.mail_content = mail_content

    class CreateMail(MysqlCRUDTemplate):
        def __init__(self, mail: Mail) -> None:
            self.mail = mail
            super().__init__()

        def execute(self):
            mail_model = MailModel(
                id=None,
                s3_object_key=self.mail.s3_object_key,
                subject=self.mail.subject,
                summary_list=self.mail.summary_list,
                newsletter_id=self.mail.newsletter_id,
                recv_at=self.mail.date,
            )
            self.session.add(mail_model)
            self.session.commit()
            self.mail.id = mail_model.id

    class ReadMailByS3ObjectKey(MysqlCRUDTemplate):
        def __init__(self, s3_object_key) -> None:
            self.s3_object_key = s3_object_key
            super().__init__()

        def execute(self):
            mail_model = (
                self.session.query(MailModel)
                .filter(MailModel.s3_object_key == self.s3_object_key)
                .first()
            )
            if not mail_model:
                return None

            mail = Mail(
                id=mail_model.id,
                s3_object_key=mail_model.s3_object_key,
                subject=mail_model.subject,
                summary_list=mail_model.summary_list,
                newsletter_id=mail_model.newsletter_id,
            )
            return mail

        def run(self) -> Mail:
            return super().run()

    class LoadMail(MysqlCRUDTemplate):
        def __init__(self, mail: Mail) -> None:
            self.mail = mail
            super().__init__()

        def execute(self):
            mail_model = (
                self.session.query(MailModel)
                .filter(MailModel.s3_object_key == self.mail.s3_object_key)
                .first()
            )
            if not mail_model:
                return None

            self.mail.id = mail_model.id
            self.mail.subject = mail_model.subject
            self.mail.summary_list = mail_model.summary_list
            self.mail.share_text = self.mail._make_share_text()
            self.mail.newsletter_id = mail_model.newsletter_id
            return True

    class UpdateMailSummaryList(MysqlCRUDTemplate):
        def __init__(self, mail: Mail) -> None:
            self.mail = mail
            super().__init__()

        def execute(self):
            mail_model = (
                self.session.query(MailModel)
                .filter(MailModel.id == self.mail.id)
                .first()
            )
            if not mail_model:
                return None
            mail_model.summary_list = self.mail.summary_list
            self.session.commit()

    class DeleteMail(MysqlCRUDTemplate):
        def __init__(self, mail: Mail) -> None:
            self.mail = mail
            super().__init__()

        def execute(self):
            mail_model = (
                self.session.query(MailModel)
                .filter(MailModel.s3_object_key == self.mail.s3_object_key)
                .first()
            )
            if not mail_model:
                return False
            self.session.delete(mail_model)
            self.session.commit()

    class ReadMailListFromNewsletter(MysqlCRUDTemplate):
        def __init__(self, newsletter: NewsLetter) -> None:
            self.newsletter = newsletter
            super().__init__()

        def execute(self):
            mail_list = list()
            mail_models = (
                self.session.query(MailModel)
                .filter(MailModel.newsletter_id == self.newsletter.id)
                .all()
            )
            if not mail_models:
                return None
            for mail_model in mail_models:
                mail = Mail(
                    id=mail_model.id,
                    s3_object_key=mail_model.s3_object_key,
                    subject=mail_model.subject,
                    summary_list=mail_model.summary_list,
                )
                mail_list.append(mail)
            return mail_list

    class ReadLastMailOfNewsltterByNewsletterID(MysqlCRUDTemplate):
        def __init__(self, newsletter_id) -> None:
            self.newsletter_id = newsletter_id
            super().__init__()

        def execute(self):
            mail_model = (
                self.session.query(MailModel)
                .filter(MailModel.newsletter_id == self.newsletter_id)
                .order_by(MailModel.recv_at.desc())
                .first()
            )
            if not mail_model:
                return False
            mail = Mail(
                id=mail_model.id,
                s3_object_key=mail_model.s3_object_key,
                subject=mail_model.subject,
                summary_list=mail_model.summary_list,
                newsletter_id=mail_model.newsletter_id,
            )
            return mail

        def run(self) -> Mail:
            return super().run()
