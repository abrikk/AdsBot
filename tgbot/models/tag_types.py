from sqlalchemy import Column, String, TIMESTAMP, func, Table, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from tgbot.services.db_base import Base


ads_tags = Table(
    "ads_tags",
    Base.metadata,
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    ),
    Column(
        "post_id",
        ForeignKey("ads.post_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    ),
)


class TagType(Base):
    __tablename__ = "tag_type"
    type = Column(String(length=128), primary_key=True)
    names = relationship(
        "TagName",
        lazy="joined"
    )
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'TagType: {self.tag_type})'
