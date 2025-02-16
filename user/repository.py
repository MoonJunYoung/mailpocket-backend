from common.database.connector import MysqlCRUDTemplate
from common.database.model import SubscribeModel, UserModel
from common.exceptions import (
    AlreadySubscribedException,
    NotSubscribedNewsletterException,
)
from user.domain import User


class UserRepository:
    class Create(MysqlCRUDTemplate):
        def __init__(
            self,
            identifier=None,
            password=None,
            platform=None,
            platform_id=None,
            is_member=None,
        ) -> None:
            super().__init__()
            self.identifier = identifier
            self.password = password
            self.platform = platform
            self.platform_id = platform_id
            self.is_member = is_member

        def execute(self):
            user_model = UserModel(
                id=None,
                identifier=self.identifier,
                password=self.password,
                platform=self.platform,
                platform_id=self.platform_id,
                is_member=self.is_member,
            )
            self.session.add(user_model)
            self.session.commit()
            return User(
                id=user_model.id,
                identifier=user_model.identifier,
                password=user_model.password,
                platform=user_model.platform,
                platform_id=user_model.platform_id,
                is_member=user_model.is_member,
            )

        def run(self) -> User:
            return super().run()

    class Update(MysqlCRUDTemplate):
        def __init__(
            self,
            id,
            identifier=None,
            password=None,
            platform=None,
            platform_id=None,
        ) -> None:
            super().__init__()
            self.id = id
            self.identifier = identifier
            self.password = password
            self.platform = platform
            self.platform_id = platform_id
            self.is_member = True

        def execute(self):
            user_model = (
                self.session.query(UserModel).filter(UserModel.id == self.id).first()
            )
            user_model.identifier = self.identifier
            user_model.password = self.password
            user_model.platform = self.platform
            user_model.platform_id = self.platform_id
            user_model.is_member = self.is_member
            self.session.commit()

            return User(
                id=user_model.id,
                identifier=user_model.identifier,
                password=user_model.password,
                platform=user_model.platform,
                platform_id=user_model.platform_id,
                is_member=user_model.is_member,
            )

        def run(self) -> User:
            return super().run()

    class ReadByIdentifier(MysqlCRUDTemplate):
        def __init__(self, identifier) -> None:
            self.identifier = identifier
            super().__init__()

        def execute(self):
            user_model = (
                self.session.query(UserModel)
                .filter(UserModel.identifier == self.identifier)
                .first()
            )
            if not user_model:
                return None
            user = User(
                id=user_model.id,
                identifier=user_model.identifier,
                password=user_model.password,
            )
            return user

    class ReadUserByPlatformID(MysqlCRUDTemplate):
        def __init__(self, platform_id, platform) -> None:
            self.platform_id = platform_id
            self.platform = platform
            super().__init__()

        def execute(self):
            user_model = (
                self.session.query(UserModel)
                .filter(UserModel.platform == self.platform)
                .filter(UserModel.platform_id == self.platform_id)
                .first()
            )
            if not user_model:
                return None
            user = User(
                id=user_model.id,
                platform_id=user_model.platform_id,
                platform=user_model.platform,
                is_member=user_model.is_member,
            )
            return user

    class ReadByID(MysqlCRUDTemplate):
        def __init__(self, id) -> None:
            self.id = id
            super().__init__()

        def execute(self):
            user_model = (
                self.session.query(UserModel).filter(UserModel.id == self.id).first()
            )
            if not user_model:
                return None
            user = User(
                id=user_model.id,
                identifier=user_model.identifier,
                password=user_model.password,
                platform_id=user_model.platform_id,
                platform=user_model.platform,
                is_member=user_model.is_member,
            )
            return user

    class CreateUserNewsletterMapping(MysqlCRUDTemplate):
        def __init__(self, user: User, newsletter_id) -> None:
            self.user = user
            self.newsletter_id = newsletter_id
            super().__init__()

        def execute(self):
            if (
                self.session.query(SubscribeModel)
                .filter(SubscribeModel.user_id == self.user.id)
                .filter(SubscribeModel.newsletter_id == self.newsletter_id)
                .first()
            ):
                raise AlreadySubscribedException
            subscribe_model = SubscribeModel(
                id=None, newsletter_id=self.newsletter_id, user_id=self.user.id
            )
            self.session.add(subscribe_model)
            self.session.commit()

    class DeleteUserNewsletterMapping(MysqlCRUDTemplate):
        def __init__(self, user: User, newsletter_id) -> None:
            self.user = user
            self.newsletter_id = newsletter_id
            super().__init__()

        def execute(self):
            subscribe_model = (
                self.session.query(SubscribeModel)
                .filter(SubscribeModel.user_id == self.user.id)
                .filter(SubscribeModel.newsletter_id == self.newsletter_id)
            ).first()
            if not subscribe_model:
                raise NotSubscribedNewsletterException
            self.session.delete(subscribe_model)
            self.session.commit()

    class CreateUserNewslettersMapping(MysqlCRUDTemplate):
        def __init__(self, user: User, newsletter_ids: list[int]) -> None:
            self.user = user
            self.newsletter_ids = newsletter_ids
            super().__init__()

        def execute(self):
            for newsletter_id in self.newsletter_ids:
                subscribe_model = SubscribeModel(
                    id=None, newsletter_id=newsletter_id, user_id=self.user.id
                )
                self.session.add(subscribe_model)
            self.session.commit()

    class DeleteUserNewslettersMapping(MysqlCRUDTemplate):
        def __init__(self, user: User) -> None:
            self.user = user
            super().__init__()

        def execute(self):
            subscribe_models = (
                self.session.query(SubscribeModel)
                .filter(SubscribeModel.user_id == self.user.id)
                .all()
            )
            for subscribe_model in subscribe_models:
                self.session.delete(subscribe_model)
            self.session.commit()
