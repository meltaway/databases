import sys
import math
import time
sys.path.append('../')

from controllers.queryController import QueryController
from CUI.cui import CUI

class QueryView:
    def __init__(self):
        self.currentMenu = None
        self.page = 1
        self.per_page = 10
        self.min = None
        self.max = None

        self.CUI = CUI("Query Menu")
        self.queryController = QueryController()
        self.CUI.addField("Search News By Rating Range", lambda: self.__getNewsByRatingRange())
        self.CUI.addField("Search News By Title Fragment", lambda: self.__getNewsByTitleFragment())
        self.CUI.addField("Get All News Tags", lambda: self.__getAllNewsTags())
        self.CUI.addField("Get All Tag Topics", lambda: self.__getAllTagTopics())

    def run(self):
        self.CUI.run()

    def __paginationParams(self, page: int, per_page: int):
        self.page = page
        self.per_page = per_page
        self.currentMenu.stop()
        self.__getNewsByRatingRange()

    def __exitMenu(self):
        self.min = None
        self.max = None
        self.page = 1
        self.per_page = 10
        self.currentMenu.stop()

    def __getNewsByRatingRange(self):
        queryMenu = CUI("News")
        self.currentMenu = queryMenu
        try:
            if self.min is None or self.max is None:
                self.min = int(input("Enter min rating: "))
                self.max = int(input("Enter max rating: "))
                if not (isinstance(self.min, int) and isinstance(self.max, int) and self.max >= self.min and self.min > 0 and self.max > 0):
                    raise Exception("Invalid input")

            start = time.time()
            rows = self.queryController.getNewsByRatingRange(self.min, self.max)
            end = time.time()

            # queryMenu.addField("News Title | Posted | Rating")
            # for row in rows:
            #     queryMenu.addField(f"\"{row[0]}\" {row[1]} *{row[2]}*")

            queryMenu.setError("\n " + str(end - start)[:9] + "s (done)\nrows: " + str(len(rows)))

            if self.page < math.ceil(len(rows) / self.per_page):
                queryMenu.addField(">>>", lambda: self.__paginationParams(self.page + 1, self.per_page))
            if self.page > 1:
                queryMenu.addField("<<<", lambda: self.__paginationParams(self.page - 1, self.per_page))

            queryMenu.addField("News Title | Posted | Rating")
            for row in self.queryController.getNewsByRatingRange(self.min, self.max, self.page, self.per_page):
                queryMenu.addField(f"\"{row[0]}\" {row[1]} *{row[2]}*")

        except Exception as err:
            queryMenu.setError(str(err))

        queryMenu.addField("Back To Previous Menu", lambda: self.__exitMenu())
        queryMenu.run(False)

    def __getAllNewsTags(self):
        queryMenu = CUI("News Tags")
        self.currentMenu = queryMenu
        try:
            nid = int(input("Enter News id: "))

            if not (isinstance(nid, int) and nid > 0):
                raise Exception("Invalid input")

            start = time.time()
            rows = self.queryController.getAllNewsTags(nid)
            end = time.time()

            queryMenu.setError("\n " + str(end - start)[:9] + "s (done)\nrows: " + str(len(rows)))

            queryMenu.addField("News Title | Tag Name")
            for row in rows:
                queryMenu.addField(f"{row[1]} ({row[0]})")

        except Exception as err:
            queryMenu.setError(str(err))

        queryMenu.run("Back To Previous Menu")

    def __getAllTagTopics(self):
        queryMenu = CUI("Tag Topics")
        self.currentMenu = queryMenu
        try:
            nid = int(input("Enter Tag id: "))

            if not (isinstance(nid, int) and nid > 0):
                raise Exception("Invalid input")

            start = time.time()
            rows = self.queryController.getAllTagTopics(nid)
            end = time.time()

            queryMenu.setError("\n " + str(end - start)[:9] + "s (done)\nrows: " + str(len(rows)))

            queryMenu.addField("Tag Name | Topic Name")
            for row in rows:
                queryMenu.addField(f"{row[1]} ({row[0]})")

        except Exception as err:
            queryMenu.setError(str(err))

        queryMenu.run("Back To Previous Menu")

    def __getNewsByTitleFragment(self):
        queryMenu = CUI("News Title Search")
        self.currentMenu = queryMenu
        try:
            frag = str(input("Enter Title Fragment: "))

            if not len(frag) > 0:
                raise Exception("Invalid input")

            start = time.time()
            rows = self.queryController.getNewsByTitleFragment(frag)
            end = time.time()

            queryMenu.setError("\n " + str(end - start)[:9] + "s (done)\nrows: " + str(len(rows)))

            queryMenu.addField(f"News Titles Containing '{frag}'")
            for row in rows:
                queryMenu.addField(f"{row[0]}")

        except Exception as err:
            queryMenu.setError(str(err))

        queryMenu.run("Back To Previous Menu")
