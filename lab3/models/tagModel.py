from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.links import links_news_tags
from database import Base
import time


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = Column(String, unique=True, nullable=False, default='news')

    # M:N relationship
    News = relationship('News', secondary=links_news_tags)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return "<Tag(name='%s')>" % self.name

# def generateRows(self, entitiesNum: int):
#     start = time.time()
#     try:
#         self.db.cursor.execute(f"INSERT  INTO tags (name)"
#                                f" SELECT generatestring(7)"
#                                f" FROM generate_series(1, {entitiesNum})")
#         self.db.connection.commit()
#         self.db.cursor.execute(f"INSERT INTO tags_topics (tag_id, topic_id) "
#                                f"SELECT getrandomrow('tags')::int, getrandomrow('topics')::int "
#                                f"FROM generate_series(1, {entitiesNum})")
#         self.db.connection.commit()
#     except Exception as err:
#         print("Generate Rows error! ", err)
#     end = time.time()
#     return str(end - start)[:9] + 's'
