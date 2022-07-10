from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, Integer

from tgbot.services.db_base import Base


class Restriction(Base):
    __tablename__ = "restrictions"
    id = Column(Integer, primary_key=True)
    restriction_name = Column(String(length=64), nullable=False)
    number = Column(BigInteger, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=func.now(),
                        onupdate=func.now(),
                        server_default=func.now())

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'Restriction (Name - Number: {self.restriction_name} - {self.number})'


