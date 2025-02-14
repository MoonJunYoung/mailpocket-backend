import datetime
import json
from email import policy
from email.parser import BytesParser

from backend.common.gpt_prompt import mail_summary


class Mail:
    def __init__(
        self,
        id,
        mail_content=None,
        s3_object_key=None,
        subject=None,
        summary_list=None,
        newsletter_id=None,
        recv_at=None,
    ) -> None:
        self.id = id
        self.mail_content = mail_content
        self.s3_object_key = s3_object_key
        self.subject = subject
        self.read_link = f"https://mailpocket.me/read?mail={self.s3_object_key}"
        self.summary_list = summary_list
        if self.summary_list:
            self.share_text = self._make_share_text()
        self.newsletter_id = newsletter_id
        self.recv_at = recv_at

    def _make_share_text(self):
        text = ""
        text += self.subject + "\n\n"
        for k, v in self.summary_list.items():
            text += "#" + k + "\n"
            text += v + "\n\n"
        text = text.rstrip("\n\n")
        return text

    def parser_eamil(self):
        parsed_email = BytesParser(policy=policy.default).parsebytes(self.mail_content)
        self.date = datetime.datetime.strftime(
            datetime.datetime.strptime(
                str(parsed_email["Date"]), "%a, %d %b %Y %H:%M:%S %z"
            ),
            "%Y-%m-%d %H:%M:%S",
        )
        from_email = str(parsed_email["From"])
        subject = str(parsed_email["Subject"])
        html_body = None
        if parsed_email.is_multipart():
            for part in parsed_email.walk():
                if part.get_content_type() == "text/html":
                    html_body = part.get_payload(decode=True).decode(
                        part.get_content_charset()
                    )
                    break
        else:
            if parsed_email.get_content_type() == "text/html":
                html_body = parsed_email.get_payload(decode=True).decode(
                    parsed_email.get_content_charset()
                )

        self.from_name = from_email.split(" <")[0]
        if '"' in self.from_name:
            self.from_name = self.from_name.replace('"', "")
        self.from_email = from_email.split(" <")[1].replace(">", "")
        self.subject = subject
        self.html_body = html_body
        del self.mail_content

    def summary(self):
        self.summary_list = mail_summary(self.from_email, self.subject, self.html_body)

    # 리펙토링 필수,, 일단 급해서
    def set_newsletter_id(self, newsletter_id):
        self.newsletter_id = newsletter_id
