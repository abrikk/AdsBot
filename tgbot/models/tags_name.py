from sqlalchemy import Column, ForeignKey, String, BigInteger, UniqueConstraint

from tgbot.services.db_base import Base


class TagName(Base):
    __tablename__ = "tag_name"
    id = Column(BigInteger, primary_key=True)
    category = Column(String(length=64), ForeignKey("tag_category.category", ondelete="CASCADE"))
    name = Column(String(length=64))
    UniqueConstraint('category', 'name', name='unique_tag_name')

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return f'TagName - category: {self.category} - name: {self.name}'
