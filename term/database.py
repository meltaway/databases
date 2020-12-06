from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('postgresql://postgres:Firestarter31@localhost:5432/news_system')
session = sessionmaker(bind=engine)()


def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
