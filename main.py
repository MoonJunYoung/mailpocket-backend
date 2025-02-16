import uvicorn
from fastapi import APIRouter, FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware

from channel.presentation import ChannelPresentation
from common import experiment
from common.token import Token
from mail.presentation import MailPresentation
from mail.service import MailService
from newsletter.presentition import NewsLetterPresentation
from user.presentation import UserPresentation
from user.service import UserService

app = FastAPI()
main_router = APIRouter()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Location"],
)


@main_router.get("/haelth-check", status_code=200)
def haelth_check():
    return "haelth_check"


user_service = UserService()
mail_service = MailService()


@main_router.get("/mails", status_code=200)
def get_mail_list():
    mail_list = mail_service.get_mail_list()
    return mail_list


@main_router.get("/mails/detail", status_code=200)
def get_mail_detail(
    mail_id: str,
):
    mail = mail_service.get_mail_detail(mail_id)
    return mail


@main_router.get("/experiment", status_code=200)
def get_fexperiment(
    Authorization=Header(None),
):
    user_id = Token.get_user_id_by_token(Authorization)
    user = user_service.read(user_id)
    features = experiment.get_experiment(user)
    return features


main_router.include_router(MailPresentation.router)
main_router.include_router(UserPresentation.router)
main_router.include_router(ChannelPresentation.router)
main_router.include_router(NewsLetterPresentation.router)
app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
