import psycopg2
import os
import sys

sys.path.append('../')
from utility.jsonParser import JsonParser


class Database:
    def __init__(self):
        config = JsonParser(os.getcwd()).getJsonObject('./config.json')
        self.connection = psycopg2.connect(database=config['database'], user=config['user'], password=config['password'], host=config['host'])
        self.cursor = self.connection.cursor()

    def defineGenerateNIDFunc(self):
        self.cursor.execute("CREATE OR REPLACE FUNCTION generateNID() RETURNS text "
                            "LANGUAGE plpgsql "
                            "AS "
                            "$$ "
                            "DECLARE outputString text; "
                            "BEGIN "
                            "SELECT concat('N', (TRUNC(floor(RANDOM() * 90000)+ 10000)::int)::text) INTO outputString; "
                            "RETURN outputString; "
                            "END; "
                            "$$; ")
        self.connection.commit()

    def defineGenerateRatingFunc(self):
        self.cursor.execute("CREATE OR REPLACE FUNCTION generateRating() RETURNS float "
                            "LANGUAGE plpgsql "
                            "AS "
                            "$$ "
                            "DECLARE outputFloat float; "
                            "BEGIN "
                            "SELECT round((RANDOM() * 5)::numeric, 1) INTO outputFloat; "
                            "RETURN outputFloat; "
                            "END; "
                            "$$")
        self.connection.commit()

    def defineGenerateStringFunc(self):
        self.cursor.execute("CREATE OR REPLACE FUNCTION generateString(length int) RETURNS text "
                            "LANGUAGE plpgsql "
                            "AS "
                            "$$ "
                            "DECLARE outputString text; "
                            "BEGIN "
                            "SELECT string_agg(chr(TRUNC(97 + RANDOM()*25)::int), '') FROM generate_series(1, length) INTO outputString; "
                            "RETURN outputString; "
                            "END; "
                            "$$; ")
        self.connection.commit()

    def defineGenerateDateFunc(self):
        self.cursor.execute("CREATE OR REPLACE FUNCTION generatedate() RETURNS text "
                            "LANGUAGE plpgsql "
                            "AS "
                            "$$ "
                            "DECLARE outputDate text;"
                            "BEGIN "
                            "SELECT concat((1990 + TRUNC(RANDOM() * 30 + 1)::int)::text, '-0', TRUNC(RANDOM() * 9 + 1)::text, '-', (8 + TRUNC(RANDOM() * 20 + 1)::int)::text) "
                            "INTO outputDate; "
                            "RETURN outputDate;"
                            "END; "
                            "$$;")
        self.connection.commit()

    def defineGenerateIntFunc(self):
        self.cursor.execute("CREATE OR REPLACE FUNCTION generateint(max integer) RETURNS text "
                            "LANGUAGE plpgsql "
                            "AS "
                            "$$ "
                            "DECLARE outputInt int; "
                            "BEGIN "
                            "SELECT TRUNC(RANDOM() * max + 1) INTO outputInt; "
                            "RETURN outputInt; "
                            "END; "
                            "$$; ")
        self.connection.commit()

    def init(self):
        self.defineGenerateStringFunc()
        self.defineGenerateDateFunc()
        self.defineGenerateIntFunc()
        self.defineGenerateNIDFunc()
        self.defineGenerateRatingFunc()