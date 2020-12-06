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

# def generateRows(self, entitiesNum: int):
#     start = time.time()
#     try:
#         self.db.cursor.execute(f"INSERT  INTO topics (name)"
#                                f" SELECT generatestring(7)"
#                                f" FROM generate_series(1, {entitiesNum})")
#         self.db.connection.commit()
#         self.db.cursor.execute(f"INSERT INTO tags_topics (tag_id, topic_id) "
#                                f"SELECT getrandomrow('topics')::int, getrandomrow('topics')::int "
#                                f"FROM generate_series(1, {entitiesNum})")
#         self.db.connection.commit()
#     except Exception as err:
#         print("Generate Rows error! ", err)
#     end = time.time()
#     return str(end - start)[:9] + 's'
