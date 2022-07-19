from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from tgbot.services.db_base import Base

ads_tags = Table(
    "ads_tags",
    Base.metadata,
    Column(
        "id",
        ForeignKey("tag_name.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    ),
    Column(
        "post_id",
        ForeignKey("ads.post_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    ),
)


class PostAd(Base):
    __tablename__ = "ads"
    status = Column(String(length=16), default="active")
    post_id = Column(BigInteger, primary_key=True)
    post_type = Column(String(length=4))
    user_id = Column(BigInteger, nullable=False)
    title = Column(String(length=128), nullable=True)
    description = Column(String(length=1024), nullable=False)
    price = Column(Integer, nullable=True)
    contacts = Column(String(length=128), nullable=False)
    currency_code = Column(String(length=3), nullable=False)
    negotiable = Column(Boolean, nullable=True)
    # photos_ids = Column(String(length=1024), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())

    tags = relationship(
        "TagName",
        secondary=ads_tags,
        lazy="selectin",
        passive_deletes="all"
    )

    related_messages = relationship(
        "RelatedMessage",
        lazy="joined"
    )

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Posted Ad (ID: {self.post_id} - {[self.__dict__]})'
