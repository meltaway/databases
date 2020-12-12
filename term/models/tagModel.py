from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.orm import relationship
from models.links import links_news_tags
from database import Base


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = Column(String, unique=True, nullable=False, default='news')

    __table_args__ = (
        Index('tags_id_idx', id),
    )

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return "<Tag(name='%s')>" % self.name
