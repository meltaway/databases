from sqlalchemy import func, select, update
from sqlalchemy.orm.attributes import InstrumentedAttribute
from database import session
from models.ratingsModel import Rating
from models.newsModel import News


class EntityController(object):
    def __init__(self, instance):
        self.instance = instance

    def getPaginated(self, page: int, per_page: int):
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

            if self.instance.__name__ == 'News':
                session.execute(f"INSERT INTO news_tags (tag_id, news_id) "
                                f"SELECT getrandomrow('tags')::int, {item.id} ")
                session.commit()
            return item.id
        except Exception as err:
            raise ValueError("Add error: " + str(err))

    def delete(self, id):
        try:
            tbd = self.getById(id)
            if tbd is None:
                raise Exception(f"Entity by id ({id}) does not exist")
            if self.instance.__name__ == 'News':
                session.execute(f"DELETE FROM news_tags WHERE news_id = {id}; ")
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
            if type(key_type) is InstrumentedAttribute and key != 'id' and not key[0].isupper():
                keys.append(key)
        return keys

    def getEntityMappedKeys(self, item):
        mapped_values = {}
        for entity in item.__dict__.items():
            key = entity[0]
            value = entity[1]
            if key != '_sa_instance_state' and key != 'id':
                mapped_values[key] = value
        return mapped_values
