from sqlalchemy import BigInteger, Column, String, ForeignKey

from tgbot.services.db_base import Base


class PostIds(Base):
    __tablename__ = "post_ids"
    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey("ads.post_id", ondelete="CASCADE"))
    message_id = Column(BigInteger, nullable=True)

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Main ID (ID: {self.main_id} - {self.another_ids})'
