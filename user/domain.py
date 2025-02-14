class User:
    def __init__(
        self,
        id,
        identifier=None,
        password=None,
        platform=None,
        platform_id=None,
        is_member=None,
    ) -> None:
        self.id = id
        self.identifier = identifier
        self.password = password
        self.platform = platform
        self.platform_id = platform_id
        self.is_member = is_member
