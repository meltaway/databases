from models.newsModel import News
from models.tagModel import Tag
from models.topicModel import Topic
from sqlalchemy import func, select
from database import session
import datetime

class QueryController(object):
    def __init__(self, instance):
        self.instance = instance

    def getNewsByRatingRange(self, minr: float, maxr: float, *args):
        try:
            count = session.execute(select([func.count()]).select_from(self.instance)).scalar()
            if len(args) == 0 or count < args[1]:
                stmt = select(News.id, News.title, News.date, News.rating).select_from(News)\
                    .where(News.rating >= minr, News.rating <= maxr)
                res = session.execute(stmt).all()
                return res
            else:
                stmt = select(News.id, News.title, News.date, News.rating).select_from(News)\
                    .where(News.rating >= minr, News.rating <= maxr)\
                    .limit(args[1])\
                    .offset(args[0] * args[1])
                res = session.execute(stmt).all()
                return res
        except Exception as err:
            raise TypeError(str(err))

    def getNewsByTitleFragment(self, tit: str, *args):
        try:
            count = session.execute(select([func.count()]).select_from(self.instance)).scalar()
            if len(tit) == 0:
                raise ValueError("Incorrect word length")

            if len(args) == 0 or count < args[1]:
                stmt = select(News.id, News.title, News.date, News.rating).where(News.title.like('%' + str(tit) + '%'))
                res = session.execute(stmt).all()
                return res
            else:
                stmt = select(News.id, News.title, News.date, News.rating)\
                    .where(News.title.like('%' + str(tit) + '%')) \
                    .limit(args[1]) \
                    .offset(args[0] * args[1])
                res = session.execute(stmt).all()
                return res
        except Exception as err:
            raise TypeError(str(err))

    def getNewsByDateRange(self, mind: datetime, maxd: datetime, *args):
        try:
            count = session.execute(select([func.count()]).select_from(self.instance)).scalar()
            if len(args) == 0 or count < args[1]:
                stmt = f"SELECT id, title, date, rating FROM news " \
                       f"WHERE date >= '{mind.strftime('%Y-%m-%d')}' AND date <= '{maxd.strftime('%Y-%m-%d')}'"
                res = session.execute(stmt).all()
                return res
            else:
                stmt = f"SELECT id, title, date, rating FROM news " \
                       f"WHERE date >= '{mind.strftime('%Y-%m-%d')}' AND date <= '{maxd.strftime('%Y-%m-%d')}' " \
                       f"LIMIT {args[1]} " \
                       f"OFFSET {args[0] * args[1]}"
                res = session.execute(stmt).all()
                return res
        except Exception as err:
            raise TypeError(str(err))

    def getAllNewsTags(self, nid: int, *args):
        try:
            count = session.execute(select([func.count()]).select_from(self.instance)).scalar()
            if len(args) == 0 or count < args[1]:
                return session.query(Tag.id, Tag.name).join(News.Tags).filter(News.id == nid).all()
            else:
                res = session.query(Tag.id, Tag.name).join(News.Tags).filter(News.id == nid)\
                    .limit(args[1])\
                    .offset(args[0] * args[1]).all()
                return res
        except Exception as err:
            raise TypeError(str(err))

    def getAllTagTopics(self, tid: int, *args):
        try:
            count = session.execute(select([func.count()]).select_from(self.instance)).scalar()
            if len(args) == 0 or count < args[1]:
                return session.query(Topic.id, Topic.name).select_from(Topic).where(Topic.tag_id == tid).all()
            else:
                stmt = session.query(Topic.id, Topic.name).select_from(Topic).where(Topic.tag_id == tid)\
                    .limit(args[1])\
                    .offset(args[0] * args[1]).all()
                res = session.execute(stmt).all()
                return res
        except Exception as err:
            raise TypeError(str(err))
