from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer, \
    Boolean, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from tgbot.services.db_base import Base


class PostAd(Base):
    __tablename__ = "ads"
    post_id = Column(BigInteger, primary_key=True)
    post_type = Column(String(length=16))
    user_id = Column(BigInteger, nullable=False)
    tag_category = Column(String(length=64))
    tag_name = Column(String(length=64))
    description = Column(String(length=1024), nullable=False)
    price = Column(Integer, nullable=True)
    contacts = Column(String(length=128), nullable=False)
    currency_code = Column(String(length=3), nullable=False)
    negotiable = Column(Boolean, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())
    ForeignKeyConstraint(["tag_category", "tag_name"], ["tag_name.category", "tag_name.name"])

    related_messages = relationship(
        "RelatedMessage",
        lazy="joined",
        cascade="all, delete, delete-orphan"
    )

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Posted Ad (ID: {self.post_id} - {[self.__dict__]})'
