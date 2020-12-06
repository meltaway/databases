from sqlalchemy import func, select
from sqlalchemy.orm.attributes import InstrumentedAttribute
from database import session
from sqlalchemy import text

class ModelController(object):
    def __init__(self, instance):
        self.instance = instance

    def generateNews(self, n: int):
        session.query(text(f"INSERT INTO news (date, title, category, description, rating)"
                               f"SELECT generatedate()::date,"
                               f"generatestring(30),"
                               f"generatestring(10),"
                               f"generatestring(100),"
                               f"generaterating()"
                               f"FROM generate_series(1, {n})"
                               f"ORDER BY generatedate()"))
        session.commit()
        session.query(f"INSERT INTO news_tags (tag_id, news_id)"
                               f"SELECT getrandomrow('tags')::int, getrandomrow('news')::int "
                               f"FROM generate_series(1, {n})")
        session.commit()

    def getPaginate(self, page: int, per_page: int):
        items = []
        try:
            page -= 1
            items = session.query(self.instance).order_by(self.instance.id.asc()).offset(page * per_page).limit(per_page).all()
        except Exception as err:
            print("getPaginate error: ", err)
            raise err
        return items

    def getById(self, id):
        try:
            return session.query(self.instance).get(id)
        except Exception as err:
            print("getById error: ", err)
            raise err

    def add(self, item):
        try:
            if not isinstance(item, self.instance):
                raise Exception("Invalid arguments")
            session.add(item)
            session.commit()
            session.refresh(item)
            return item.id
        except Exception as err:
            print("Add error: ", err)
            raise err

    def delete(self, id):
        try:
            tbd = self.getById(id)
            if tbd is None:
                raise Exception(f"Entity by id ({id}) does not exist")
            session.query(self.instance).filter(self.instance.id == id).delete()
            session.commit()
            return tbd
        except Exception as err:
            print("Delete error: ", err)
            raise err


    def update(self, item):
        try:
            if not isinstance(item, self.instance):
                raise Exception("Invalid arguments")

            session.query(self.instance).filter(self.instance.id == item.id).update(self.getModelEntityMappedKeys(item))
            session.commit()
            return True
        except Exception as err:
            print("Update error: ", err)
            raise err

    def getCount(self):
        try:
            return session.execute(select([func.count()]).select_from(self.instance)).scalar()
        except Exception as err:
            print("getCount error: ", err)
            raise err

    def getModelKeys(self):
        keys = []
        for entity in self.instance.__dict__.items():
            key = entity[0]
            key_type = entity[1]
            if type(key_type) is InstrumentedAttribute and key != 'id' and not key[0].isupper():
                keys.append(key)
        return keys

    def getModelEntityMappedKeys(self, item):
        mapped_values = {}
        for entity in item.__dict__.items():
            key = entity[0]
            value = entity[1]
            if key != '_sa_instance_state':
                mapped_values[key] = value
        return mapped_values
