from sqlalchemy import Column, BigInteger, ForeignKey

from tgbot.services.db_base import Base


class RelatedMessage(Base):
    __tablename__ = "related_message"
    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey("ads.post_id", ondelete="CASCADE"))
    message_id = Column(BigInteger, nullable=False)

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Main ID (ID: {self.post_id} - {self.message_id})'
