from mail.domain import Mail


class NewsLetter:
    def __init__(
        self,
        id,
        name,
        category_id,
        send_date,
        mail: Mail = None,
        mails: list[Mail] = None,
        operating_status=None,
    ) -> None:
        self.id = id
        self.name = name
        self.category_id = category_id
        self.send_date = send_date
        self.mail = mail
        self.mails = mails
        self.operating_status = operating_status


class Category:
    def __init__(self, id, name, operating_status=False) -> None:
        self.id = id
        self.name = name
        self.operating_status = operating_status

    def check_newsletter_vaild(self, newsletter_list: list[NewsLetter]):
        # 전체카테고리 정상처리를 위한 하드코딩
        if not self.id:
            self.operating_status = True
            return True
        for newsletter in newsletter_list:
            if newsletter.category_id == self.id:
                if newsletter.operating_status:
                    self.operating_status = True
                    return True
