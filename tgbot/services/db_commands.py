from datetime import datetime

import pytz
from sqlalchemy import select, or_, update, and_, func, String, extract

from tgbot.constants import TIMEZONE, TIME_TO_ASK
from tgbot.models.post_ad import PostAd
from tgbot.models.restriction import Restriction
from tgbot.models.tag_category import TagCategory
from tgbot.models.tags_name import TagName
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

    async def get_user_max_active(self, user_id: int):
        sql = select(User.max_active).where(User.user_id == user_id)
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
                    User.last_name.ilike(f"%{like}%"),
                    User.username.ilike(f"%{like}%"),
                    User.user_id.cast(String).ilike(f"%{like}%"),
                    User.created_at.cast(String).ilike(f"%{like}%")
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

    async def get_value_of_restriction(self, uid: str):
        sql = select(Restriction.number).where(Restriction.uid == uid)
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def get_tag_categories(self) -> list[TagCategory]:
        sql = select(TagCategory.id, TagCategory.category).where(
            TagCategory.category.in_(select(TagName.category).distinct())
        )
        request = await self.session.execute(sql)
        return request.all()

    async def get_tag_category(self, id: int | str):
        sql = select(TagCategory.category).where(TagCategory.id == int(id))
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def get_tag_names(self, category: str) -> list[TagName]:
        sql = select(TagName).where(TagName.category == category).order_by(TagName.id)
        request = await self.session.execute(sql)
        return request.scalars().all()

    async def get_my_ads(self, user_id: int):
        sql = select(
            PostAd.description,
            PostAd.post_id
        ).where(
            and_(
                PostAd.user_id == user_id,
                PostAd.updated_at.is_not(None)  # PostAd.created_at + TIME_TO_ASK > datetime.now()
            )
        ).order_by(PostAd.created_at)
        request = await self.session.execute(sql)
        return request.all()

    async def get_tags(self):
        sql = select(TagName.category, TagName.name)
        request = await self.session.execute(sql)
        return request.all()

    async def get_tags_of_category(self, category: str):
        sql = select(TagName.id, TagName.name).where(TagName.category == category)
        request = await self.session.execute(sql)
        return request.all()

    async def get_categories(self):
        sql = select(TagCategory.id, TagCategory.category)
        request = await self.session.execute(sql)
        return request.all()

    async def get_tags_by_category_and_name(self, category: str, name: str):
        sql = select(TagName.id).where(
            and_(
                TagName.category == category,
                TagName.name == name
            )
        )
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def get_user_posts_ids(self, user_id: int):
        sql = select(PostAd.post_id).where(PostAd.user_id == user_id)
        request = await self.session.execute(sql)
        return request.scalars().all()

    async def get_support_team(self, user_ids: list[int]):
        sql = select(
            User.user_id, User.first_name,
            User.last_name, User.username
        ).where(
            and_(
                User.role.in_(['owner', 'admin']),
                User.user_id.in_(user_ids)
            )
        )
        request = await self.session.execute(sql)
        return request.all()

    async def get_support_team_ids(self):
        sql = select(
            User.user_id
        ).where(User.role.in_(['owner', 'admin']))
        request = await self.session.execute(sql)
        return request.scalars().all()

    async def get_post_limit(self):
        sql = select(Restriction.number).where(Restriction.uid == 'post')
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def count_user_active_ads(self, user_id: int):
        sql = select(func.count("*")).select_from(PostAd).where(
            PostAd.user_id == user_id
        )
        request = await self.session.execute(sql)
        return request.scalars().first()

    # statistics
    async def count_users(self, condition: str = "all"):
        options: dict = {
            "all": True,
            "day": and_(
                extract("DAY", User.created_at) == datetime.now(tz=pytz.timezone(TIMEZONE)).day,
                extract("MONTH", User.created_at) == datetime.now(tz=pytz.timezone(TIMEZONE)).month,
                extract("YEAR", User.created_at) == datetime.now(tz=pytz.timezone(TIMEZONE)).year
            ),
            "month": and_(
                extract("MONTH", User.created_at) == datetime.now(tz=pytz.timezone(TIMEZONE)).month,
                extract("YEAR", User.created_at) == datetime.now(tz=pytz.timezone(TIMEZONE)).year
            ),
            "admin": User.role == "admin",
            "banned": User.role == "banned",
            "restricted": User.restricted_till.is_not(None),
        }
        sql = select(func.count("*")).select_from(User).where(options[condition])
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def count_ads(self, condition: str = "all"):
        options: dict = {
            "all": True,
            "day": extract("DAY", PostAd.created_at) == datetime.now(tz=pytz.timezone(TIMEZONE)).day,
            "month": extract("MONTH", PostAd.created_at) == datetime.now(tz=pytz.timezone(TIMEZONE)).month,
            "sell": PostAd.post_type == "sell",
            "buy": PostAd.post_type == "buy",
            "rent": PostAd.post_type == "rent",
            "occupy": PostAd.post_type == "occupy",
            "exchange": PostAd.post_type == "exchange",
        }
        sql = select(func.count("*")).select_from(PostAd).where(options[condition])
        request = await self.session.execute(sql)
        return request.scalars().first()

    async def is_ad_like_this_exist(self, user_id: int, description: str, tag_category: str, tag_name: str, price: int,
                                    currency_code: str, post_type: str):
        sql = select(PostAd).select_from(PostAd).where(
            and_(
                PostAd.user_id == user_id,
                PostAd.description == description,
                PostAd.tag_category == tag_category,
                PostAd.tag_name == tag_name,
                PostAd.price == price,
                PostAd.currency_code == currency_code,
                PostAd.post_type == post_type
            )
        )
        request = await self.session.execute(sql)
        return request.scalars().first()
