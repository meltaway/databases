import sys
sys.path.append('../')
import math
from controllers.newsController import NewsController
from models.newsModel import News
from CUI.cui import CUI

class NewsView:
    def __init__(self):
        self.currentMenu = [None, None]
        self.page = 1
        self.per_page = 10

        self.CUI = CUI("News Model Menu")
        self.newsController = NewsController()
        self.CUI.addField("News", lambda: self.__getAllNews())
        self.CUI.addField("Add News Piece", lambda: self.__addNews())
        self.CUI.addField("Generate Rows", lambda: self.__generateRows())

    def run(self):
        self.CUI.run()

    def __getAllNews(self):
        newsMenu = CUI("News")
        self.currentMenu[0] = newsMenu
        try:
            if self.page < math.ceil(self.newsController.getCount() / self.per_page):
                newsMenu.addField(">>>", lambda: self.__paginationParams(self.page + 1, self.per_page))
            if self.page > 1:
                newsMenu.addField("<<<", lambda: self.__paginationParams(self.page - 1, self.per_page))
            products = self.newsController.getAll(self.page, self.per_page)
            for news in products:
                newsMenu.addField(f"{news.title} ({news.date})", lambda id=news.id: self.__getNews(id))

        except Exception as err:
            newsMenu.setError(str(err))
        newsMenu.run("Back To Main Menu")

    def __getNews(self, id: str):
        newsMenu = CUI("News Piece Menu")
        self.currentMenu[1] = newsMenu
        try:
            news: News = self.newsController.getById(id)
            values = news.getValues().split(',')
            keys = news.getKeys().split(',')
            for i in range(len(keys)):
                newsMenu.addField(keys[i] + ' : ' + values[i])

            newsMenu.addField("DELETE", lambda: self.__deleteNews(news.id))
            newsMenu.addField("UPDATE", lambda: self.__updateNews(news.id))
            newsMenu.addField("Back To Previous Menu", lambda: self.__supportCUIFunc())
        except Exception as err:
            newsMenu.setError(str(err))
        newsMenu.run(False)

    def __addNews(self):
        try:
            result = self.newsController.add()
            if isinstance(result, bool) and not result:
                raise Exception("Incorrect values")
            else:
                self.CUI.setError("New News id: " + str(result))
        except Exception as err:
            self.CUI.setError(str(err))

    def __updateNews(self, id: int):
        if self.newsController.update(id):
            self.currentMenu[1].stop()
            self.__getNews(id)
        else:
            self.currentMenu[1].setError("Incorrect update values")

    def __deleteNews(self, id: int):
        self.newsController.delete(id)
        self.currentMenu[1].stop()
        self.__supportCUIFunc()

    def __generateRows(self):
        try:
            n = int(input("Enter number of rows to generate: "))
            if not (isinstance(n, int) and n > 0):
                raise Exception("Invalid input")
            self.CUI.setError("Please wait...")
            time = self.newsController.generateRows(n)
            self.CUI.setError(time + " (done)")
        except Exception as error:
            self.CUI.setError(str(error))

    def __paginationParams(self, page: int, per_page: int):
        self.page = page
        self.per_page = per_page
        self.currentMenu[0].stop()
        self.__getAllNews()

    def __supportCUIFunc(self):
        self.currentMenu[1].stop()
        self.__paginationParams(self.page, self.per_page)
