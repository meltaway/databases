from database import session


class RandomController(object):
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
