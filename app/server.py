import json
import bcrypt

from aiohttp import web
from models import init_orm, engine, Session, User, Advert
from sqlalchemy.exc import IntegrityError

from scheme import CreateAdvert, CreateUser
from tools import validate


app = web.Application()


async def hash_password(password):
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password


def check_password(password, hashed_password):
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.checkpw(password, hashed_password)


async def init_db(app):
    print("init db")
    await init_orm()
    yield
    print("close db")
    await engine.dispose()


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(init_db)
app.middlewares.append(session_middleware)


def get_http_error(error_class, text):
    return error_class(
        text=json.dumps({"error": text}), content_type="application/json"
    )


async def get_user_by_id(session: Session, user_id: int):
    user = await session.get(User, user_id)
    if user is None:
        raise get_http_error(web.HTTPNotFound, "User not found")
    return user


async def add_user(session: Session, user: User):
    try:
        session.add(user)
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, "User already exists")
    return user.id


class UserView(web.View):
    @property
    def session(self) -> Session:
        return self.request.session

    @property
    def user_id(self):
        return int(self.request.match_info["user_id"])

    async def get_user(self):
        return await get_user_by_id(self.session, self.user_id)

    async def get(self):
        user = await self.get_user()
        return web.json_response(user.dict)

    async def post(self):
        json_data = await self.request.json()
        json_data = validate(CreateUser, json_data)
        json_data["password"] = await hash_password(json_data["password"])
        user = User(**json_data)
        await add_user(self.session, user)
        return web.json_response({"id": user.id})

    async def delete(self):
        user = await self.get_user()
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


async def get_advert_by_id(session: Session, advert_id: int):
    advert = await session.get(Advert, advert_id)
    if advert is None:
        raise get_http_error(web.HTTPNotFound, "Advert not found")
    return advert


async def add_advert(session: Session, advert: Advert):
    try:
        session.add(advert)
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, "Advert already exists")
    return advert.id


def check_authority(user: User, advert: Advert):
    if user.id != advert.owner_id:
        raise get_http_error(web.HTTPForbidden, "User is not the owner")


class AdvertView(web.View):
    @property
    def session(self) -> Session:
        return self.request.session

    @property
    def advert_id(self):
        return int(self.request.match_info["advert_id"])

    async def get_advert(self):
        return await get_advert_by_id(self.session, self.advert_id)

    async def get(self):
        advert = await self.get_advert()
        return web.Response(text=advert.to_json, content_type="application/json")

    async def post(self):
        json_data = await self.request.json()
        json_data = validate(CreateAdvert, json_data)
        advert = Advert(**json_data)
        await add_advert(self.session, advert)
        return web.json_response({"id": advert.id})

    async def delete(self):
        advert = await self.get_advert()
        payload = await self.request.json()
        user_id = int(payload.get("owner_id", 0))
        check_authority(await get_user_by_id(self.session, user_id), advert)
        await self.session.delete(advert)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


app.add_routes(
    [
        web.get("/advert/{advert_id:\d+}", AdvertView),
        web.delete("/advert/{advert_id:\d+}", AdvertView),
        web.post("/advert", AdvertView),
        web.get("/user/{user_id:\d+}", UserView),
        web.delete("/user/{user_id:\d+}", UserView),
        web.post("/user", UserView),
    ]
)

web.run_app(app, port=8080)
