from ast import literal_eval

from aredis_om.model.model import NotFoundError
from fastapi import APIRouter, HTTPException, Query, Response
from neu_sdk.config import LOGGER
from neu_sdk.security import check_password

from neu_users.schemas import (
    User,
    UserCreate,
    UserPasswordUpdate,
    UserPublic,
    UserPublicRestricted,
    UserUpdate,
)

router = APIRouter(tags=["users"], responses={404: {"description": "Not found"}})


@router.post("/", response_model=UserPublic)
async def create_user(data: UserCreate) -> UserPublic:
    try:
        await User.find(
            (User.username == data.username) | (User.email == data.email)
        ).first()
        raise HTTPException(403, "User already exists")
    except NotFoundError as e:
        pass
    except HTTPException as e:
        raise e
    except Exception as e:
        LOGGER.warning(e)

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
    expression = [(User.superuser == False)]

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
async def get_user(*, pk: str) -> UserPublic:
    try:
        return await User.get(pk)
    except NotFoundError as e:
        raise HTTPException(404, f"User {pk} not found") from e


@router.patch("/{pk}", response_model=UserPublic)
async def update_user(
    *,
    pk: str,
    data: UserUpdate,
    overwrite: bool = Query(False, description="Overwrite extra data"),
) -> UserPublic:
    user = await get_user(pk=pk)

    if data.extra is not None:
        if user.extra is not None and not overwrite:
            extra = literal_eval(user.extra)
            extra.update(data.extra)
            data.extra = extra
        data.extra = str(data.extra)

    await user.update(**data.model_dump(exclude_none=True, exclude_unset=True))
    await user.save()
    return user


@router.patch("/password/{pk}", response_model=UserPublic)
async def update_password(*, pk: str, data: UserPasswordUpdate) -> UserPublic:
    user = await get_user(pk=pk)

    if not check_password(data.old_password, user.password):
        raise HTTPException(404, "Not Permitted")

    await user.update(password=data.password)
    await user.save()
    return user


@router.delete("/{pk}")
async def delete_user(*, pk: str) -> Response:
    # TODO Delete all dependencies
    user = await get_user(pk=pk)

    if user.superuser:
        raise HTTPException(404, "Superuser cannot be deleted")

    await User.delete(pk)
    return Response("Deleted")
