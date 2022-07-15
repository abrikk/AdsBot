from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from tgbot.models.tag import ads_tags
from tgbot.services.db_base import Base


class PostAd(Base):
    __tablename__ = "ads"
    status = Column(String(length=16), default="active")
    post_id = Column(BigInteger, primary_key=True)
    post_type = Column(String(length=4))
    user_id = Column(BigInteger, nullable=False)
    description = Column(String(length=1024), nullable=False)
    contacts = Column(String(length=128), nullable=False)
    price = Column(Integer, nullable=True)
    currency_code = Column(String(length=3), nullable=False)
    negotiable = Column(Boolean, nullable=True)
    title = Column(String(length=128), nullable=True)
    photos_ids = Column(String(length=512), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())

    tags = relationship(
        "Tag",
        secondary=ads_tags,
        lazy="selectin"
    )

    related_messages = relationship(
        "RelatedMessage",
        lazy="joined"
    )

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Posted Ad (ID: {self.post_id} - {[self.__dict__]})'
