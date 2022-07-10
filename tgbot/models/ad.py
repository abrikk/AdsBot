from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer
from sqlalchemy.orm import relationship

from tgbot.models.administration import ads_administration
from tgbot.services.db_base import Base


class Ads(Base):
    __tablename__ = "ads"
    post_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    tags = Column(String(length=64), nullable=False)
    description = Column(String(length=1024), nullable=False)
    contacts = Column(String(length=128), nullable=False)
    price = Column(Integer, nullable=True)
    title = Column(String(length=128), nullable=True)
    photos_ids = Column(String(length=512), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())

    administration_table = relationship(
        "Administration",
        secondary=ads_administration,
        back_populates="administration"
    )

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Management (ID: {self.common_id} - {[self.__dict__]})'
