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


def defineIndeces():
    session.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm; "
                    "CREATE INDEX title_gin_idx ON news USING gin(title gin_trgm_ops);"
                    "CREATE INDEX date_brin_idx ON news USING brin(date); "
                    "CREATE INDEX news_id_index ON news(id); "
                    "CREATE INDEX tags_id_index ON tags(id); "
                    "CREATE INDEX topics_id_index ON topics(id); "
                    "CREATE INDEX link_id_index ON news_tags(tag_id, news_id); "
                    "CREATE INDEX ratings_id_index ON ratings(id); ")
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


def insertStarterEntities():
    session.execute("INSERT INTO news (id, date, title, category, description, rating) "
                    "VALUES(1, '1970-01-01', 'A Good Title', 'news', 'A good description.', 5.0); "
                    "INSERT INTO tags (id, name) VALUES (1, 'news'); "
                    "INSERT INTO news_tags (tag_id, news_id) VALUES (1, 1); "
                    "INSERT INTO topics (id, name, tag_id) VALUES (1, 'general', 1);")
    session.commit()

def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    defineGenerateDateFunc()
    defineGenerateStringFunc()
    defineGenerateIntFunc()
    defineGenerateRatingFunc()
    defineRatingTrigger()
    insertStarterEntities()
