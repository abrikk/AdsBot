from sqlalchemy import BigInteger, Column, String

from tgbot.services.db_base import Base


class PostIds(Base):
    __tablename__ = "post_ids"
    main_id = Column(BigInteger, primary_key=True)
    another_ids = Column(String(length=512), nullable=True)

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Main ID (ID: {self.main_id} - {self.another_ids})'
