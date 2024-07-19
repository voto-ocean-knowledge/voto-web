from datetime import datetime
from typing import Optional
from passlib.hash import pbkdf2_sha256 as crypto
from voto.data.db_classes import User


def hash_text(text: str) -> str:
    hashed_text = crypto.hash(text, rounds=128000)
    return hashed_text


def find_user_by_email(email: str) -> Optional[User]:
    return User.objects(email=email).first()


def verify_hash(hashed_text: str, plain_text: str) -> bool:
    return crypto.verify(plain_text, hashed_text)


def create_user(name: str, email: str, password: str) -> Optional[User]:
    if find_user_by_email(email):
        return None
    user = User()
    if len(User.objects().order_by("user_id")) == 0:
        user.user_id = 1
    else:
        user.user_id = User.objects().order_by("-user_id").first().user_id + 1
    user.name = name
    user.email = email
    user.hashed_password = hash_text(password)
    user.date_added = datetime.now()
    user.last_login = datetime.now()
    user.save()
    return user


def login_user(email: str, password: str) -> Optional[User]:

    user = find_user_by_email(email)
    if not user:
        return None
    if not verify_hash(user.hashed_password, password):
        return None
    user.last_login = datetime.now()
    user.save()
    return user


def find_user_by_id(user_id: int) -> Optional[User]:
    return User.objects(user_id=user_id).first()
