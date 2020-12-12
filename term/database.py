from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('postgresql://postgres:Firestarter31@localhost:5432/news_system')
session = sessionmaker(bind=engine)()


def defineGenerateRatingFunc():
    session.execute("CREATE OR REPLACE FUNCTION generaterating() RETURNS float "
                        "LANGUAGE plpgsql "
                        "AS "
                        "$$ "
                        "DECLARE outputFloat float; "
                        "BEGIN "
                        "SELECT round((RANDOM() * 5)::numeric, 1) INTO outputFloat; "
                        "RETURN outputFloat; "
                        "END; "
                        "$$")
    session.commit()


def defineGenerateStringFunc():
    session.execute("CREATE OR REPLACE FUNCTION generatestring(length int) RETURNS text "
                        "LANGUAGE plpgsql "
                        "AS "
                        "$$ "
                        "DECLARE outputString text; "
                        "BEGIN "
                        "SELECT string_agg(chr(TRUNC(97 + RANDOM()*25)::int), '') FROM generate_series(1, length) INTO outputString; "
                        "RETURN outputString; "
                        "END; "
                        "$$; ")
    session.commit()


def defineGenerateDateFunc():
    session.execute("CREATE OR REPLACE FUNCTION generatedate() RETURNS text "
                        "LANGUAGE plpgsql "
                        "AS "
                        "$$ "
                        "DECLARE outputDate text; "
                        "BEGIN "
                        "WITH last_date AS (SELECT date FROM news ORDER BY id DESC LIMIT 1) "
                        "SELECT ((SELECT * FROM last_date)::timestamp + '1 day'::interval)::date::text "
                        "INTO outputDate;"
                        "RETURN outputDate; "
                        "END; "
                        "$$;")
    session.commit()


def defineGenerateIntFunc():
    session.execute("CREATE OR REPLACE FUNCTION generateint(max integer) RETURNS text "
                        "LANGUAGE plpgsql "
                        "AS "
                        "$$ "
                        "DECLARE outputInt int; "
                        "BEGIN "
                        "SELECT TRUNC(RANDOM() * max + 1) INTO outputInt; "
                        "RETURN outputInt; "
                        "END; "
                        "$$; ")
    session.commit()


def defineGetRandomRow():
    execStr = "\'SELECT id FROM \"%s\"\' || \'ORDER BY RANDOM()\' || \'LIMIT 1\'"
    session.execute(f"CREATE OR REPLACE FUNCTION getrandomrow(tname text) RETURNS text "
                    f"LANGUAGE plpgsql "
                    f"AS "
                    f"$$ "
                    f"DECLARE output int;"
                    f"BEGIN "
                    f"EXECUTE format({execStr}, tname) "
                    f"INTO output; "
                    f"RETURN output; "
                    f"END; "
                    f"$$;")
    session.commit()


def defineExtensions():
    session.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm; CREATE EXTENSION IF NOT EXISTS btree_gin; ")
    session.commit()

def defineRatingTrigger():
    session.execute("CREATE OR REPLACE FUNCTION generation_rating_trigger() RETURNS trigger AS "
                    "$$ "
                    "BEGIN "
                    "INSERT INTO ratings(news_id, date, rating) VALUES (New.id, now()::timestamp, New.rating); "
                    "return New; "
                    "END; "
                    "$$ "
                    "LANGUAGE plpgsql; "
                    "CREATE TRIGGER generation_rating_trigger AFTER INSERT OR UPDATE ON news "
                    "FOR EACH ROW EXECUTE PROCEDURE generation_rating_trigger()")
    session.commit()


def defineTagTrigger():
    cursor1 = "curu NO SCROLL CURSOR FOR SELECT topics.id, tag_id FROM topics INNER JOIN tags t ON t.id = topics.tag_id WHERE tag_id = New.id ORDER BY topics.id;"
    cursor2 = "curd NO SCROLL CURSOR FOR SELECT topics.id, tag_id FROM topics INNER JOIN tags t ON t.id = topics.tag_id WHERE tag_id = Old.id ORDER BY topics.id;"
    session.execute(f"CREATE OR REPLACE FUNCTION tag_trigger() RETURNS trigger AS "
                    f"$$ "
                    f"DECLARE "
                    f"{cursor1} "
                    f"{cursor2} "
                    f"record record; "
                    f"BEGIN IF (TG_OP = 'UPDATE') THEN "
                    f"OPEN curu; "
                    f"LOOP "
                    f"FETCH curu INTO record; "
                    f"IF NOT found THEN EXIT; END IF; "
                    f"UPDATE topics SET tag_id = 0 WHERE record.id = topics.id; "
                    f"END LOOP; "
                    f"RETURN New; "
                    f"END IF; "
                    f"IF (TG_OP = 'DELETE') THEN "
                    f"IF Old.id = 1 THEN RAISE EXCEPTION 'The general news tag cannot be deleted'; END IF; "
                    f"OPEN curd; LOOP FETCH curd INTO record; "
                    f"IF NOT found THEN EXIT; END IF; "
                    f"UPDATE topics SET tag_id = 1 WHERE record.id = topics.id; "
                    f"END LOOP; "
                    f"RETURN Old; "
                    f"END IF; "
                    f"END; "
                    f"$$ LANGUAGE plpgsql; "
                    f"CREATE TRIGGER tag_trigger BEFORE UPDATE OR DELETE ON tags FOR EACH ROW EXECUTE PROCEDURE tag_trigger()")
    session.commit()


def insertStarterEntities():
    session.execute("INSERT INTO news (id, date, title, category, description, rating) "
                    "VALUES(1, '1970-01-01', 'A Good Title', 'news', 'A good description.', 5.0); "
                    "INSERT INTO tags (id, name) VALUES (1, 'news'); "
                    "INSERT INTO news_tags (tag_id, news_id) VALUES (1, 1); "
                    "INSERT INTO topics (id, name, tag_id) VALUES (1, 'general', 1);")
    session.commit()


def autoincremetFix():
    session.execute("ALTER SEQUENCE news_id_seq RESTART 2; "
                    "ALTER SEQUENCE tags_id_seq RESTART 2; "
                    "ALTER SEQUENCE topics_id_seq RESTART 2; "
                    "ALTER SEQUENCE ratings_id_seq RESTART 2; ")
    session.commit()

def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    defineGenerateDateFunc()
    defineGenerateStringFunc()
    defineGenerateIntFunc()
    defineGenerateRatingFunc()
    defineGetRandomRow()
    defineExtensions()
    defineRatingTrigger()
    defineTagTrigger()
    insertStarterEntities()
    autoincremetFix()
