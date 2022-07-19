from sqlalchemy import Column, ForeignKey, String, BigInteger

from tgbot.services.db_base import Base


class TagName(Base):
    __tablename__ = "tag_name"
    id = Column(BigInteger, primary_key=True)
    type = Column(String(length=128), ForeignKey("tag_type.type", ondelete="CASCADE"))
    name = Column(String(length=128))

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'POST ID (ID: {self.post_id} - {self.message_id})'
