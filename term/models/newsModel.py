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

    def __init__(self, date: str, title: str, category: str, description: str, rating: float):
        self.date = date
        self.title = title
        self.category = category
        self.description = description
        self.rating = rating

    def __repr__(self):
        return "<News(date='%s', title='%s', category='%s', description='%s', rating='%f')>"\
               % (self.date, self.title, self.category, self.description, self.rating)

# def generateRows(self, n: int):
#     start = time.time()
#     try:
#         self.db.cursor.execute(f"INSERT INTO news (date, title, category, description, rating)"
#                                f"SELECT generatedate()::date,"
#                                f"generatestring(30),"
#                                f"generatestring(10),"
#                                f"generatestring(100),"
#                                f"generaterating()"
#                                f"FROM generate_series(1, {n})")
#         self.db.connection.commit()
#         self.db.cursor.execute(f"INSERT INTO news_tags (tag_id, news_id)"
#                                f"SELECT getrandomrow('tags')::int, getrandomrow('news')::int "
#                                f"FROM generate_series(1, {n})")
#         self.db.connection.commit()
#     except Exception as err:
#         print("generation error:", err)
#         exit(1)
#     end = time.time()
#     return str(end - start)[:9] + 's'
