from sqlalchemy import Column, String, TIMESTAMP, func
from sqlalchemy.orm import relationship

from tgbot.services.db_base import Base


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
