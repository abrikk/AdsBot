from sqlalchemy import select

from tgbot.models.restriction import Restriction
from tgbot.models.tag import Tag
from tgbot.models.user import User


class DBCommands:
    def __init__(self, session):
        self.session = session

    async def get_user(self, user_id: int):
        sql = select(User).where(User.user_id == user_id)
        request = await self.session.execute(sql)
        user = request.scalar()
        return user

    async def add_user(self,
                       user_id: int,
                       first_name: str,
                       last_name: str = None,
                       username: str = None,
                       role: str = 'user'
                       ) -> 'User':
        user = User(user_id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    role=role)
        self.session.add(user)
        return user

    async def get_restrictions(self):
        sql = select(Restriction).order_by(Restriction.order)
        request = await self.session.execute(sql)
        return request.scalars().all()

    async def get_values_of_restrictions(self):
        sql = select(Restriction.number).order_by(Restriction.order)
        request = await self.session.execute(sql)
        return request.scalars().all()

    async def get_tags(self):
        sql = select(Tag.tag_name).order_by(Tag.created_at.desc())
        request = await self.session.execute(sql)
        return request.scalars().all()
