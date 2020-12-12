from sqlalchemy import Column, Integer, Float, Date, func, String, Index
from sqlalchemy.orm import relationship, backref
from models.links import links_news_tags
from database import Base


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False, default=func.now())
    title = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False, default='news')
    description = Column(String)
    rating = Column(Float, nullable=False, default=0.0)

    # 1:M relationship
    Ratings = relationship('Rating', cascade="all, delete", passive_deletes=True)
    # M:N relationship
    Tags = relationship('Tag', secondary=links_news_tags, backref='news')

    __table_args__ = (
        Index('title_gin_idx', "title", postgresql_ops={"title": "gin_trgm_ops"}, postgresql_using='gin'),
        Index('date_brin_idx', "date", postgresql_using='brin'),
        Index('news_id_idx', id),
    )

    def __init__(self, date: str, title: str, category: str, description: str, rating: float):
        self.date = date
        self.title = title
        self.category = category
        self.description = description
        self.rating = rating

    def __repr__(self):
        return "<News(date='%s', title='%s', category='%s', description='%s', rating='%f')>"\
               % (self.date, self.title, self.category, self.description, self.rating)
