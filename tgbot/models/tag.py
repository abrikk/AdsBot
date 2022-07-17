from sqlalchemy import Column, String, TIMESTAMP, func, Table, ForeignKey

from tgbot.services.db_base import Base


ads_tags = Table(
    "ads_tags",
    Base.metadata,
    Column(
        "tag_name",
        ForeignKey("tags.tag_name", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    ),
    Column(
        "post_id",
        ForeignKey("ads.post_id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True
    ),
)


class Tag(Base):
    __tablename__ = "tags"
    tag_name = Column(String(length=100), primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Tag (ID: {self.tag_name} - {[self.__dict__]})'
