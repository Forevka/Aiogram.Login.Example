import collections
import hashlib
import hmac

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from config import BOT_TOKEN, ENVIRONMENT
from fake_db import FakeRepo
from models import TelegramAuthModel

app = FastAPI()
if (ENVIRONMENT != 'debug'):
    app.root_path = '/api/auth_server/'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    ...


def check_user_data(data: TelegramAuthModel, token):
    secret = hashlib.sha256()
    secret.update(token.encode('utf-8'))
    sorted_params = collections.OrderedDict(sorted(data.dict().items()))
    msg = "\n".join(["{}={}".format(k, v)
                    for k, v in sorted_params.items() if k != 'hash'])

    return data.hash == hmac.new(secret.digest(), msg.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()


async def login_route(request: Request, user: TelegramAuthModel = Depends()) -> Response:
    if (ENVIRONMENT.lower().strip() == "production"):
        if (not check_user_data(user, BOT_TOKEN)):
            raise HTTPException(status_code=401, detail="Nice try hacker :D")

    user_from_database = FakeRepo().get_user(user.id)

    if (user_from_database["role_id"] == 2):
        raise HTTPException(
            status_code=401, detail="Sorry you don't have permission")

    return templates.TemplateResponse("login.html", {
        "request": request,
        **user.dict()
    })


templates = Jinja2Templates(directory="templates")

app.add_api_route(
    '/auth',
    login_route,
    tags=['Authorize'],
    methods=['GET'],
    response_class=HTMLResponse,
)
