from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship

from tgbot.services.db_base import Base


ads_tags = Table(
    "ads_tags",
    Base.metadata,
    Column(
        "tag_name",
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "post_id",
        ForeignKey("ads.post_id", ondelete="CASCADE"),
        primary_key=True
    ),
)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    tag_name = Column(String(length=100), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())
    tags = relationship(
        "Ads",
        secondary=ads_tags,
        back_populates="ads"
    )

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Management (ID: {self.common_id} - {[self.__dict__]})'


