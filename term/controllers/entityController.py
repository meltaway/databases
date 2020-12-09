from sqlalchemy import func, select, update
from sqlalchemy.orm.attributes import InstrumentedAttribute
from database import session

class EntityController(object):
    def __init__(self, instance):
        self.instance = instance

    def generateNews(self, n: int):
        try:
            session.execute(f"INSERT INTO news (date, title, category, description, rating) "
                               f"SELECT generatedate()::date, "
                               f"generatestring(30), "
                               f"generatestring(10), "
                               f"generatestring(100), "
                               f"generaterating() "
                               f"FROM generate_series(1, {n}) "
                               f"ORDER BY generatedate()")
            session.commit()
            session.execute(f"INSERT INTO news_tags (tag_id, news_id) "
                               f"SELECT getrandomrow('tags')::int, getrandomrow('news')::int "
                               f"FROM generate_series(1, {n})")
            session.commit()
        except Exception as err:
            raise ValueError("generateNews error: " + str(err))
        return True

    def generateTags(self, n: int):
        try:
            session.execute(f"INSERT INTO tags (name)"
                               f" SELECT generatestring(7)"
                               f" FROM generate_series(1, {n})")
            session.commit()
        except Exception as err:
            raise ValueError("generateTags error: " + str(err))
        return True

    def generateTopics(self, n: int):
        try:
            session.execute(f"INSERT INTO topics (name, tag_id)"
                               f" SELECT generatestring(7), getrandomrow('tags')::int"
                               f" FROM generate_series(1, {n})")
            session.commit()
        except Exception as err:
            raise ValueError("generateTopics error: " + str(err))
        return True

    def getPaginate(self, page: int, per_page: int):
        items = []
        try:
            page -= 1
            items = session.query(self.instance).order_by(self.instance.id.asc()).offset(page * per_page).limit(per_page).all()
        except Exception as err:
            raise ValueError("getPaginate error: " + str(err))
        return items

    def getById(self, id):
        try:
            return session.query(self.instance).get(id)
        except Exception as err:
            raise ValueError("getById error: " + str(err))

    def add(self, item):
        try:
            if not isinstance(item, self.instance):
                raise Exception("Invalid arguments")
            session.add(item)
            session.commit()
            session.refresh(item)
            return item.id
        except Exception as err:
            raise ValueError("Add error: " + str(err))

    def delete(self, id):
        try:
            tbd = self.getById(id)
            if tbd is None:
                raise Exception(f"Entity by id ({id}) does not exist")
            session.query(self.instance).filter(self.instance.id == id).delete()
            session.commit()
            return tbd
        except Exception as err:
            raise ValueError("Delete error: " + str(err))

    def update(self, item):
        try:
            if not isinstance(item, self.instance):
                raise Exception("Invalid arguments")

            session.query(self.instance).filter(self.instance.id == item.id).update(self.getModelEntityMappedKeys(item))
            session.commit()
            return True
        except Exception as err:
            raise ValueError("Update error: " + str(err))

    def getCount(self):
        try:
            return session.execute(select([func.count()]).select_from(self.instance)).scalar()
        except Exception as err:
            raise ValueError("getCount error: " + str(err))

    def getModelKeys(self):
        keys = []
        for entity in self.instance.__dict__.items():
            key = entity[0]
            key_type = entity[1]
            if type(key_type) is InstrumentedAttribute and key is not 'id' and key is not 'past_rating_sum' and key is not 'history_num' and not key[0].isupper():
                keys.append(key)
        return keys

    def getModelEntityMappedKeys(self, item):
        mapped_values = {}
        for entity in item.__dict__.items():
            key = entity[0]
            value = entity[1]
            if key != '_sa_instance_state' and key != 'id' and key != 'past_rating_sum' and key != 'history_num':
                mapped_values[key] = value
        return mapped_values
