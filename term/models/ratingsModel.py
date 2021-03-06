from sqlalchemy import Column, Integer, Float, ForeignKey, func, TIMESTAMP, Index
from sqlalchemy.orm import relationship, backref
from database import Base


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    news_id = Column(Integer, ForeignKey('news.id', ondelete="CASCADE"))
    date = Column(TIMESTAMP, nullable=False, default=func.now())
    rating = Column(Float, nullable=False, default=0.0)

    __table_args__ = (
        Index('ratings_id_idx', id),
    )

    def __init__(self, news_id: int, date: str, rating: float):
        self.news_id = news_id
        self.date = date
        self.rating = rating

    def __repr__(self):
        return "<Rating(news_id='%i', date='%s', rating='%f')>" % (self.news_id, self.date, self.rating)
