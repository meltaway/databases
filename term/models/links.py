from sqlalchemy import Column, Integer, Table, ForeignKey
from database import Base

links_news_tags = Table(
    'news_tags', Base.metadata,
    Column('tag_id', Integer, ForeignKey('tags.id')),
    Column('news_id', Integer, ForeignKey('news.id'))
)