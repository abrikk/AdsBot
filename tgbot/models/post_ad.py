from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from tgbot.models.tag import ads_tags
from tgbot.services.db_base import Base

post_id_ad = Table(
    "post_id_ad",
    Base.metadata,
    Column(
        "main_id",
        ForeignKey("post_ids.main_id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "post_id",
        ForeignKey("ads.post_id", ondelete="CASCADE"),
        primary_key=True
    ),
)


class PostAd(Base):
    __tablename__ = "ads"
    status = Column(String(length=16), default="active")
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

    post_id = relationship(
        "PostIds",
        secondary=post_id_ad,
        lazy="selectin"
    )

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Posted Ad (ID: {self.post_id} - {[self.__dict__]})'
