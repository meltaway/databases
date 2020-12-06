import sys
sys.path.append('../')
from database import Database

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
                self.db.cursor.execute(f"SELECT title, date, rating FROM news "
                                       f"WHERE rating > {min} AND rating < {max} "
                                       f"ORDER BY rating")
                return self.db.cursor.fetchall()
            else:
                self.db.cursor.execute(f"SELECT title, date, rating FROM news "
                                       f"WHERE rating > {min} AND rating < {max} "
                                       f"ORDER BY rating "
                                       f"LIMIT {args[1]} "
                                       f"OFFSET {args[0] * args[1]}")
                return self.db.cursor.fetchall()
        except Exception as err:
            print("getRating error: ", err)

    def getNewsByTitleFragment(self, tit: str):
        try:
            if len(tit) == 0:
                raise Exception("Incorrect word length")
            self.db.cursor.execute(f"SELECT title FROM news "
                                   f"WHERE title LIKE '%{str(tit)}%'")
            return self.db.cursor.fetchall()
        except Exception as err:
            raise str(err)

    def getAllNewsTags(self, nid: int):
        try:
            self.db.cursor.execute(f"SELECT t.name, n.title FROM tags AS t "
                                   f"INNER JOIN news_tags AS nt ON t.id = nt.tag_id "
                                   f"INNER JOIN news AS n ON n.id = nt.news_id "
                                   f"WHERE n.id = {nid}")
            return self.db.cursor.fetchall()
        except Exception as err:
            raise str(err)

    def getAllTagTopics(self, tid: int):
        try:
            self.db.cursor.execute(f"SELECT top.name, t.name FROM topics AS top "
                                   f"INNER JOIN tags_topics AS tt ON top.id = tt.topic_id "
                                   f"INNER JOIN tags AS t ON t.id = tt.tag_id "
                                   f"WHERE t.id = {tid}")
            return self.db.cursor.fetchall()
        except Exception as err:
            raise str(err)