from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.links import links_news_tags
from database import Base


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = Column(String, unique=True, nullable=False, default='news')

    # M:N relationship
    News = relationship('News', secondary=links_news_tags, overlaps='News.Tags')

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return "<Tag(name='%s')>" % self.name
