import sys
import time
sys.path.append('../')
from models.tagModel import Tag
from database import Database


class TagController(object):
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
            self.db.cursor.execute(f"SELECT {Tag().getKeys()} FROM tags ORDER BY id LIMIT {per_page} OFFSET {page * per_page}")
            rows = self.db.cursor.fetchall()
            for row in rows:
                tmp = Tag()
                tmp.parse(row)
                items.append(tmp)
        except Exception as err:
            print("getAll error: ", err)
            exit(1)
        return items

    def getById(self, tid):
        item = Tag()
        try:
            if isinstance(tid, int):
                tid = str(tid)
            if not isinstance(tid, str):
                raise Exception("Incorrect arguments")

            self.db.cursor.execute(f"SELECT {item.getKeys()} FROM tags WHERE id = {tid}")
            row = self.db.cursor.fetchone()
            if row is not None:
                item.parse(row)
            else:
                raise Exception(f"No entry with ID {tid} found")
        except Exception as err:
            print("getById error: ", err)
        return item

    def add(self, *args):
        try:
            item: Tag = Tag()
            if len(args) > 0 and isinstance(args[0], Tag):
                item = args[0]
            else:
                item.fill()

            if item.isFull():
                self.db.cursor.execute(f"INSERT INTO tags ({item.getKeys()}) VALUES ({item.getValues()}) RETURNING id as tid; ")
                self.db.connection.commit()
                id = int(self.db.cursor.fetchone()[0])
                self.db.cursor.execute(f"INSERT INTO tags_topics (tag_id, topic_id) VALUES ({id}, getrandomrow('topics')::int)")
                self.db.connection.commit()
                return id
        except Exception as err:
            print("add error: ", err)
        return False

    def delete(self, tid):
        try:
            if isinstance(tid, int): 
                tid = str(tid)
            if not isinstance(tid, str): 
                raise Exception("Incorrect arguments")

            item = self.getById(tid)
            self.db.cursor.execute(f"DELETE FROM tags WHERE id = {tid}")
            self.db.connection.commit()
            return item
        except Exception as err:
            print("delete error: ", err)
            return False

    def update(self, *args):
        try:
            item: Tag = Tag()
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

            if isinstance(args[0], Tag):
                item = args[0]

            if not item.isFull():
                raise Exception("Invalid input")

            query = ''
            keys = item.getKeys().split(',')
            values = item.getValues().split(',')
            for i in range(len(keys)):
                query += keys[i] + ' = ' + values[i] + ', '
            self.db.cursor.execute(f"UPDATE tags SET {query[:-2]} WHERE id = {item.id}")
            self.db.connection.commit()
            return True
        except Exception as err:
            print("update error: ", err)
            return False

    def getCount(self):
        try:
            self.db.cursor.execute(f"SELECT COUNT(*) FROM tags")
            return int(self.db.cursor.fetchone()[0])
        except Exception as err:
            print("getCount error: ", err)

    def generateRows(self, entitiesNum: int):
        start = time.time()
        try:
            self.db.cursor.execute(f"INSERT  INTO tags (name)"
                                   f" SELECT generatestring(7)"
                                   f" FROM generate_series(1, {entitiesNum})")
            self.db.connection.commit()
            self.db.cursor.execute(f"INSERT INTO tags_topics (tag_id, topic_id) "
                                   f"SELECT getrandomrow('tags')::int, getrandomrow('topics')::int "
                                   f"FROM generate_series(1, {entitiesNum})")
            self.db.connection.commit()
        except Exception as err:
            print("Generate Rows error! ", err)
        end = time.time()
        return str(end - start)[:9] + 's'
