import sys
sys.path.append('../')
from database import Database
from models.newsModel import News
from sqlalchemy import select

class QueryController(object):
    def __init__(self):
        try:
            self.db = Database()
            if Database is None:
                raise Exception('No connection. Please, check your config.json or Postgre server')

        except Exception as err:
            print("Connection error! ", err)
            exit(1)

    def getNewsByRatingRange(self, min: int, max: int, *args):
        try:
            if len(args) == 0:
                stmt = select(News.title, News.date, News.rating)\
                    .where(News.rating > min, News.rating < max)\
                    .order_by(News.rating)
                res = self.db.session.query(stmt)
                return res.scalars().all()
            else:
                stmt = select(News.title, News.date, News.rating)\
                    .where(News.rating > min, News.rating < max)\
                    .order_by(News.rating)\
                    .limit(args[1])\
                    .offset(args[0] * args[1])
                res = self.db.session.query(stmt)
                return res.scalars().all()
        except Exception as err:
            print("getRating error: ", err)

    def getNewsByTitleFragment(self, tit: str):
        try:
            if len(tit) == 0:
                raise Exception("Incorrect word length")
            stmt = select(News.title).where(News.title.like('%' + str(tit) + '%'))
            res = self.db.session.query(stmt)
            return res.scalars().all()
        except Exception as err:
            raise str(err)

    def getAllNewsTags(self, nid: int):
        try:
            # self.db.cursor.execute(f"SELECT t.name, n.title FROM tags AS t "
            #                        f"INNER JOIN news_tags AS nt ON t.id = nt.tag_id "
            #                        f"INNER JOIN news AS n ON n.id = nt.news_id "
            #                        f"WHERE n.id = {nid}")
            # return self.db.cursor.fetchall()
            return 0
        except Exception as err:
            raise str(err)

    def getAllTagTopics(self, tid: int):
        try:
            stmt = select(Topic.name).where(Topic.tag_id == tid)
            res = self.db.session.query(stmt)
            return res.scalars().all()
        except Exception as err:
            raise str(err)
