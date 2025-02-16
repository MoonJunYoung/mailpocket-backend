import bcrypt

from common.exceptions import (
    IdentifierAlreadyException,
    IdentifierNotFoundException,
    PasswordNotMatchException,
)
from user.domain import User
from user.repository import UserRepository


class UserService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()

    def sign_up(self, identifier, password):
        if self.user_repository.ReadByIdentifier(identifier=identifier).run():
            raise IdentifierAlreadyException(identifier)

        encrypted_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        user = self.user_repository.Create(
            identifier=identifier, password=encrypted_password, is_member=True
        ).run()
        return user

    def sign_in(self, identifier, password):
        user: User = self.user_repository.ReadByIdentifier(identifier).run()
        if not user:
            raise IdentifierNotFoundException(identifier=identifier)
        if not bcrypt.checkpw(password.encode(), user.password.encode()):
            raise PasswordNotMatchException(identifier=identifier, password=password)
        return user

    def read(self, user_id):
        user: User = self.user_repository.ReadByID(user_id).run()
        del user.password
        return user

    def create_non_member_user(self):
        user = self.user_repository.Create(is_member=False).run()
        return user

    def oauth_login(self, platform_id, platform):
        existing_user: User = self.user_repository.ReadUserByPlatformID(
            platform_id=platform_id,
            platform=platform,
        ).run()
        if existing_user:
            return existing_user

        user = self.user_repository.Create(
            platform_id=platform_id, platform=platform, is_member=True
        ).run()
        return user

    def upgrade_non_meber_user_to_member(
        self, user_id, identifier=None, password=None, platform_id=None, platform=None
    ):
        if identifier and password:
            if self.user_repository.ReadByIdentifier(identifier=identifier).run():
                raise IdentifierAlreadyException(identifier)

            encrypted_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            user = self.user_repository.Update(
                id=user_id, identifier=identifier, password=encrypted_password
            ).run()

        elif platform_id and platform:
            existing_user: User = self.user_repository.ReadUserByPlatformID(
                platform_id=platform_id,
                platform=platform,
            ).run()
            if existing_user:
                return existing_user

            user = self.user_repository.Update(
                id=user_id, platform_id=platform_id, platform=platform
            ).run()

        return user
