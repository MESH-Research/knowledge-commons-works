from typing import TypedDict


class UserAPI(TypedDict):
    email: str
    id: str
    username: str
    user_profile: dict
    preferences: dict
