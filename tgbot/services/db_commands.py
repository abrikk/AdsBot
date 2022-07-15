from sqlalchemy import select, or_, update, and_

from tgbot.models.post_ad import PostAd
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

    async def get_user_role(self, user_id: int):
        sql = select(User.role).where(User.user_id == user_id)
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def get_user_post_limit(self, user_id: int):
        sql = select(User.post_limit).where(User.user_id == user_id)
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def update_user_role(self, user_id: int, role: str):
        sql = update(User).where(User.user_id == user_id).values(role=role)
        result = await self.session.execute(sql)
        await self.session.commit()
        return result

    async def get_users(self, user_id: int, like: str = None, limit: int = 50, offset: int = 0):
        sql = select(User).select_from(User).where(
            and_(
                User.role != 'owner',
                User.user_id != user_id
            )
        )

        if like:
            sql = sql.where(
                or_(
                    User.first_name.ilike(f"%{like}%"),
                    User.last_name.ilike(f"%{like}%")
                )
            )

        sql = sql.order_by(User.created_at).limit(limit).offset(offset)
        result = await self.session.execute(sql)
        scalars = result.scalars().all()
        return scalars

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
        sql = select(Tag.tag_name).order_by(Tag.created_at)
        request = await self.session.execute(sql)
        return request.scalars().all()

    async def get_restriction(self, uid: str):
        sql = select(Restriction).where(Restriction.uid == uid)
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def get_value_of_restriction(self, uid: str):
        sql = select(Restriction.number).where(Restriction.uid == uid)
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def get_tags_by_name(self, tag_list: list[str]):
        sql = select(Tag).where(
            Tag.tag_name.in_(tag_list)
        ).order_by(Tag.created_at)
        request = await self.session.execute(sql)
        return request.scalars().all()

    async def get_my_ads(self, user_id: int):
        sql = select(
            PostAd.title,
            PostAd.description,
            PostAd.post_id
        ).where(PostAd.user_id == user_id)
        request = await self.session.execute(sql)
        return request.all()

    async def get_posted_ad(self, post_id: int):
        sql = select(PostAd).where(PostAd.post_id == post_id)
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def get_post_type(self, post_id: int):
        sql = select(PostAd.post_type).where(PostAd.post_id == post_id)
        request = await self.session.execute(sql)
        return request.scalars().first()
