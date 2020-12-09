from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('postgresql://postgres:Firestarter31@localhost:5432/news_system')
session = sessionmaker(bind=engine)()


def defineGenerateRatingFunc():
    session.execute("CREATE OR REPLACE FUNCTION generateRating() RETURNS float "
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
    session.execute("CREATE OR REPLACE FUNCTION generateString(length int) RETURNS text "
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
                        "DECLARE outputDate text;"
                        "BEGIN "
                        "WITH last_date AS ("
                        "SELECT date FROM news "
                        "ORDER BY id DESC "
                        "LIMIT 1) "
                        "SELECT ((SELECT * FROM last_date)::timestamp + '1 day'::interval)::date::text "
                        "INTO outputDate; "
                        "RETURN outputDate;"
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


def defineTagTrigger():
    return 0


def defineRatingTrigger():
    return 0


def defineIndeces():
    session.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm; "
                    "CREATE INDEX title_gin_idx ON news USING gin(title gin_trgm_ops);"
                    "CREATE INDEX date_brin_idx ON news USING brin(date); "
                    "CREATE INDEX news_id_index ON news(id); "
                    "CREATE INDEX tags_id_index ON tags(id); "
                    "CREATE INDEX topics_id_index ON topics(id); "
                    "CREATE INDEX link_id_index ON news_tags (tag_id, news_id);")
    session.commit()

def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    defineGenerateDateFunc()
    defineGenerateStringFunc()
    defineGenerateIntFunc()
    defineGenerateRatingFunc()
    defineTagTrigger()
    defineRatingTrigger()
