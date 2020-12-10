from models.newsModel import News
from models.tagModel import Tag
from models.topicModel import Topic
from sqlalchemy import func, select
from database import session


class QueryController(object):
    def __init__(self, instance):
        self.instance = instance

    def getNewsByRatingRange(self, minr: float, maxr: float, *args):
        try:
            if len(args) == 0:
                stmt = select(News.id, News.title, News.date, News.rating).select_from(News)\
                    .where(News.rating > minr, News.rating < maxr)
                res = session.execute(stmt).all()
                return res
            else:
                stmt = select(News.id, News.title, News.date, News.rating).select_from(News)\
                    .where(News.rating > minr, News.rating < maxr)\
                    .limit(args[1])\
                    .offset(args[0] * args[1])
                res = session.execute(stmt).all()
                return res
        except Exception as err:
            raise TypeError(str(err))

    def getNewsByTitleFragment(self, tit: str, *args):
        try:
            if len(tit) == 0:
                raise ValueError("Incorrect word length")

            if len(args) == 0:
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

    def getAllNewsTags(self, nid: int, *args):
        try:
            if len(args) == 0:
                res = session.query(Tag.id, Tag.name).join(News.Tags).filter(News.id == nid).all()
                return res
            else:
                res = session.query(Tag.id, Tag.name).join(News.Tags).filter(News.id == nid)\
                    .limit(args[1])\
                    .offset(args[0] * args[1]).all()
                return res
        except Exception as err:
            raise TypeError(str(err))

    def getAllTagTopics(self, tid: int, *args):
        try:
            if len(args) == 0:
                stmt = select(Topic.id, Topic.name).select_from(Topic).where(Topic.tag_id == tid)
                res = session.execute(stmt).all()
                return res
            else:
                stmt = select(Topic.id, Topic.name).select_from(Topic).where(Topic.tag_id == tid)\
                    .limit(args[1])\
                    .offset(args[0] * args[1]).all()
                res = session.execute(stmt).all()
                return res
        except Exception as err:
            raise TypeError(str(err))
