from sqlalchemy import Column, Integer, Float, Date, func, String
from sqlalchemy.orm import relationship
from models.links import links_news_tags
from database import Base
import time


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False, default=func.now())
    title = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False, default='news')
    description = Column(String)
    rating = Column(Float, nullable=False, default=0.0)

    # M:N relationship
    Tags = relationship('Tag', secondary=links_news_tags)

    def __init__(self, date: str, title: str, category: str, description: str, rating: float, past_rating_sum: float, history_num: int):
        self.date = date
        self.title = title
        self.category = category
        self.description = description
        self.rating = rating
        self.past_rating_sum = past_rating_sum
        self.history_num = history_num

    def __repr__(self):
        return "<News(date='%s', title='%s', category='%s', description='%s', rating='%f', past_rating_sum='%f', history_num='%i')>"\
               % (self.date, self.title, self.category, self.description, self.rating, self.past_rating_sum, self.history_num)
