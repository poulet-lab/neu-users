from sys import _getframe
from logging import getLogger
from bcrypt import checkpw
from fastapi import APIRouter, HTTPException, Response, Query
from aredis_om.model.model import NotFoundError

from .settings import settings
from .schema import (
    User,
    UserPublic,
    UserCreate,
    UserUpdate,
    UserPublicRestricted,
    UserPasswordUpdate,
)

_LOGGER = getLogger(f"{settings.service_name}.routes")

router = APIRouter(responses={404: {"description": "Not found"}})


@router.post("/", response_model=User)
async def create_user(data: UserCreate) -> UserPublic:
    if await User.find(
        (User.username == data.username) | (User.email == data.email)
    ).all():
        raise HTTPException(404, "User already exists")
    data = User.model_validate(data)
    await data.save()
    return data


@router.get("/all", response_model=list[UserPublicRestricted])
async def get_users(
    *,
    name: str = Query(""),
    username: str = Query(""),
    email: str = Query(""),
    search: str = Query(""),
    offset: int = Query(0),
    limit: int = Query(100),
) -> list[UserPublicRestricted]:
    expression = []

    if name:
        expression += [(User.first_name % f"*{name}*") | (User.last_name % f"*{name}*")]
    if username:
        expression += [User.username % f"*{username}*"]
    if email:
        expression += [User.email % f"*{email}*"]
    if search:
        expression += [User.extra % f"*{search}*"]

    users = await User.find(*expression).page(offset=offset, limit=limit)

    return users


@router.get("/{pk}", response_model=UserPublic)
async def get_user(pk: str) -> UserPublic:
    try:
        return await User.get(pk)
    except NotFoundError as e:
        _LOGGER.error(f"{_getframe().f_code.co_name}: {e}")
        raise HTTPException(404, "Not Found")


@router.patch("/{pk}", response_model=UserPublic)
async def update_user(
    pk: str,
    data: UserUpdate,
    overwrite: bool = Query(False, description="Overwrite extra data"),
) -> UserPublic:
    user = await User.get(pk)

    if data.extra is not None:
        if user.extra is not None and not overwrite:
            extra = eval(user.extra)
            extra.update(data.extra)
            data.extra = extra
        data.extra = str(data.extra)

    await user.update(**data.model_dump(exclude_none=True, exclude_unset=True))
    await user.save()
    return user


@router.patch("/password/{pk}", response_model=UserPublic)
async def update_password(pk: str, data: UserPasswordUpdate) -> UserPublic:
    user = await User.get(pk)

    if not checkpw(data.old_password.encode(), user.password.encode()):
        raise HTTPException(404, "Not Permitted")

    await user.update(password=data.password)
    await user.save()
    return user


@router.delete("/{pk}")
async def delete_user(pk: str) -> Response:
    user = await User.get(pk)
    if user.superuser:
        raise HTTPException(404, "Superuser cannot be deleted")
    await User.delete(pk)
    return Response("Deleted")