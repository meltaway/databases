import sys
import time
sys.path.append('../')
from models.newsModel import News
from database import Database

class NewsController(object):
    def __init__(self):
        try:
            self.db = Database()
            if Database is None: 
                raise Exception("No connection. Please, check your PostgreSQL server or config file")
        except Exception as err:
            print("Connection error: ", err)
            exit(1)

    def getAll(self, page: int, per_page: int):
        items = []
        try:
            page -= 1
            self.db.cursor.execute(f"SELECT {News().getKeys()} FROM news ORDER BY id LIMIT {per_page} OFFSET {page * per_page}")
            rows = self.db.cursor.fetchall()
            for row in rows:
                tmp = News()
                tmp.parse(row)
                items.append(tmp)
        except Exception as err:
            print("getAll error: ", err)
        return items

    def getById(self, nid):
        item = News()
        try:
            if isinstance(nid, int):
                nid = str(nid)
            if not isinstance(nid, str): 
                raise Exception("Incorrect arguments")
            
            self.db.cursor.execute(f"SELECT {item.getKeys()} from news WHERE id = {nid}")
            row = self.db.cursor.fetchone()
            if row is not None:
                item.parse(row)
            else:
                raise Exception(f"No news with ID {nid} found")
        except Exception as err:
            print("getById error: ", err)
        return item

    def add(self, *args):
        try:
            item: News = News()
            if len(args) > 0 and isinstance(args[0], News):
                item = args[0]
            else:
                item.fill()

            if item.isFull():
                self.db.cursor.execute(f"INSERT INTO news ({item.getKeys()}) VALUES ({item.getValues()}) RETURNING id;")
                self.db.connection.commit()
                id = int(self.db.cursor.fetchone()[0])
                self.db.cursor.execute(f"INSERT INTO news_tags (tag_id, news_id) VALUES (getrandomrow('tags')::int, {id})")
                self.db.connection.commit()
                return id
        except Exception as err:
            print("add error: ", err)
        return False

    def delete(self, nid):
        try:
            if isinstance(nid, int):
                nid = str(nid)
            if not isinstance(nid, str):
                raise Exception("Incorrect arguments")

            item = self.getById(nid)
            self.db.cursor.execute(f"DELETE from news WHERE id = {nid}")
            self.db.connection.commit()
            return item
        except Exception as err:
            print("delete error: ", err)
            return False

    def update(self, *args):
        try:
            item: News = News()
            if len(args) is 0:
                raise Exception("Invalid arguments")
            if isinstance(args[0], int) or isinstance(int(args[0]), int):
                item.fill()
                item.id = args[0]
                values = item.getValues().split(',')
                old_values = self.getById(args[0]).getValues().split(',')
                keys = item.getKeys().split(',')
                for i in range(len(keys)):
                    if values[i] == 'null':
                        item.__setattr__(keys[i], old_values[i])

            if isinstance(args[0], News):
                item = args[0]

            if not item.isFull():
                raise Exception("Invalid input")

            query = ''
            keys = item.getKeys().split(',')
            values = item.getValues().split(',')
            for i in range(len(keys)):
                query += keys[i] + ' = ' + values[i] + ', '
            self.db.cursor.execute(f"UPDATE news SET {query[:-2]} WHERE id = {item.id}")
            self.db.connection.commit()
            return True
        except Exception as err:
            print("update error: ", err)
            return False

    def getCount(self):
        try:
            self.db.cursor.execute(f"SELECT COUNT(*) FROM news")
            return int(self.db.cursor.fetchone()[0])
        except Exception as err:
            print("getCount error: ", err)

    def generateRows(self, n: int):
        start = time.time()
        try:
            self.db.cursor.execute(f"INSERT INTO news (date, title, category, description, rating)"
                                   f"SELECT generatedate()::date,"
                                   f"generatestring(30),"
                                   f"generatestring(10),"
                                   f"generatestring(100),"
                                   f"generaterating()"
                                   f"FROM generate_series(1, {n})"
                                   f"ORDER BY generatedate()")
            self.db.connection.commit()
            self.db.cursor.execute(f"INSERT INTO news_tags (tag_id, news_id)"
                                   f"SELECT getrandomrow('tags')::int, getrandomrow('news')::int "
                                   f"FROM generate_series(1, {n})")
            self.db.connection.commit()
        except Exception as err:
            print("generation error:", err)
            exit(1)
        end = time.time()
        return str(end - start)[:9] + 's'
