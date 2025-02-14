from backend.mail.repository import MailRepository
from backend.newsletter.domain import Category, NewsLetter
from backend.newsletter.repository import NewsLetterRepository
from backend.user.repository import UserRepository


class NewsLetterlDTO:
    def __init__(self, newsletter: NewsLetter) -> None:
        self.id = newsletter.id
        self.name = newsletter.name
        self.category_id = newsletter.category_id
        self.mail = newsletter.mail
        self.mails = newsletter.mails


class NewsLetterService:
    def __init__(self) -> None:
        self.newsletter_repository = NewsLetterRepository()
        self.user_repository = UserRepository()
        self.mail_repository = MailRepository()

    def newsletter_subscribe(self, user_id, newsletter_id):
        user = self.user_repository.ReadByID(user_id).run()
        self.user_repository.CreateUserNewsletterMapping(user, newsletter_id).run()

    def newsletter_subscribe_cancel(self, user_id, newsletter_id):
        user = self.user_repository.ReadByID(user_id).run()
        self.user_repository.DeleteUserNewsletterMapping(user, newsletter_id).run()

    def newsletters_subscribe(self, user_id, newsletter_ids):
        user = self.user_repository.ReadByID(user_id).run()
        self.user_repository.DeleteUserNewslettersMapping(user).run()
        self.user_repository.CreateUserNewslettersMapping(user, newsletter_ids).run()

    def get_newsletters(
        self, user_id, subscribe_status, sort_type, in_mail, cursor, category_id
    ):
        newsletter_list = list()
        user = self.user_repository.ReadByID(user_id).run()
        newsletters = self.newsletter_repository.ReadFilteredNewsletters(
            user, subscribe_status, sort_type, in_mail, cursor, category_id
        ).run()
        if newsletters:
            for newsletter in newsletters:
                newsletter_list.append(NewsLetterlDTO(newsletter))
        return newsletter_list

    def get_newsletter_with_previous_mail_list_by_newsletter_id(self, newsletter_id):
        newsletter = self.newsletter_repository.LoadNewsLetterByIDWithMails(
            newsletter_id
        ).run()
        return NewsLetterlDTO(newsletter)

    def get_category_list(self):
        category_list: list[Category] = (
            self.newsletter_repository.ReadCategoriesOfNewsletter().run()
        )
        newsletter_list: list[NewsLetter] = (
            self.newsletter_repository.ReadAllNewsletters().run()
        )
        for category in category_list:
            category.check_newsletter_vaild(newsletter_list)

        return category_list
