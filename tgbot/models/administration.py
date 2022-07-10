from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer

from tgbot.services.db_base import Base


class Administration(Base):
    __tablename__ = "administration"
    id = Column(Integer, primary_key=True)
    common_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=True)
    tag_name = Column(String(length=100), nullable=True)
    tag_limit = Column(Integer, nullable=True)
    contacts_limit = Column(Integer, nullable=True)
    pic_limit = Column(Integer, nullable=True)
    post_limit = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Management (ID: {self.common_id} - {[self.__dict__]})'
