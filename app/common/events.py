from pydantic import BaseModel


class UserRegistration(BaseModel):
    user_id: int
