from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from common.exceptions import catch_exception
from mail.service import MailService

mail_service = MailService()


class S3MailRecvData(BaseModel):
    s3_object_key: str


def recv_background_task(s3_object_key):
    mail_service.recv(
        s3_object_key=s3_object_key,
    )


class MailPresentation:
    router = APIRouter(prefix="/mail")

    @router.post("/recv", status_code=200)
    async def recv_mail(
        request: Request,
        background_tasks: BackgroundTasks,
        s3_email_recv_data: S3MailRecvData,
    ):
        background_tasks.add_task(
            recv_background_task, s3_email_recv_data.s3_object_key
        )
        return "I received an email. Summary tasks run in the background."

    @router.get("", status_code=200)
    async def read_mail(request: Request, key: str):
        try:
            mail = mail_service.read(
                s3_object_key=key,
            )
            return mail
        except Exception as e:
            catch_exception(e, request)

    @router.patch("summary-again", status_code=204)
    async def summary_again(request: Request, key: str):
        try:
            mail_service.summary_again(
                s3_object_key=key,
            )
        except Exception as e:
            catch_exception(e, request)
