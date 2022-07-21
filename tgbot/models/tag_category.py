from sqlalchemy import Column, String, TIMESTAMP, func, BigInteger

from tgbot.services.db_base import Base


class TagCategory(Base):
    __tablename__ = "tag_category"
    id = Column(BigInteger, primary_key=True)
    category = Column(String(length=64), unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'TagCategory ({self.category})'
