from pydantic import BaseModel

class TelegramAuthModel(BaseModel):
    id: int
    first_name: str
    username: str
    photo_url: str
    auth_date: int
    hash: str