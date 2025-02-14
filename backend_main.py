from fastapi import APIRouter, FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.channel.presentation import ChannelPresentation
from backend.common import experiment
from backend.common.token import Token
from backend.mail.presentation import MailPresentation
from backend.newsletter.presentition import NewsLetterPresentation
from backend.user.presentation import UserPresentation
from backend.user.service import UserService

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
    uvicorn.run("backend_main:app", host="0.0.0.0", port=8000, reload=True)
