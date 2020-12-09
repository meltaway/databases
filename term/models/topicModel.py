from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base
import time

class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = Column(String, unique=True, nullable=False, default='news')
    tag_id = Column(Integer, ForeignKey('tags.id'))

    # 1:M relationship
    Tag = relationship('Tag', backref=backref('Topic', uselist=False))

    def __init__(self, name: str, tag_id: int):
        self.name = name
        self.tag_id = tag_id

    def __repr__(self):
        return "<Topic(name='%s', tag_id='%i')>" % (self.name, self.tag_id)

