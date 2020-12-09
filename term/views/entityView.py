import math
from controllers.entityController import EntityController
from controllers.queryController import QueryController
from CUI.cui import CUI

exec_bad_chars = set('{}()[],;+*\/')

class EntityView:
    def __init__(self, instance):
        self.instance = instance

        self.page = 1
        self.tags_page = 1
        self.topics_page = 1
        self.title_page = 1
        self.rating_page = 1
        self.per_page = 10

        self.itemsCurrentMenu = [None, None]

        self.CUI = CUI(f"{self.instance.__name__} Menu")
        self.EController = EntityController(instance)
        self.QController = QueryController(instance)

        self.CUI.addField(f"Add {self.instance.__name__}", lambda: self.__add())
        self.CUI.addField(f"{self.instance.__name__}", lambda: self.__getItems())
        self.CUI.addField("Generate rows", lambda: self.__generateRows())

        if self.instance.__name__ == "News":
            self.CUI.addField("Search by title fragment", lambda: self.__searchNewsTitle())
            self.CUI.addField("Search by rating range", lambda: self.__searchNewsRating())


    def __generateRows(self):
        itemMenu = CUI(self.instance.__name__)
        self.itemsCurrentMenu[1] = itemMenu
        try:
            n = int(input("Enter number of rows to generate: "))
            if not (isinstance(n, int) and n > 0):
                raise Exception("Invalid input")

            if self.instance.__name__ == "News":
                if not self.EController.generateNews(n):
                    raise Exception("Could not generate news!")
            if self.instance.__name__ == "Tag":
                if not self.EController.generateTags(n):
                    raise Exception("Could not generate tags!")
            if self.instance.__name__ == "Topic":
                if not self.EController.generateTopics(n):
                    raise Exception("Could not generate topics!")

            self.itemsCurrentMenu[1].stop()
            self.__supportCUIFunc()
        except Exception as err:
            itemMenu.setError(str(err))

    def __getItems(self):
        itemMenu = CUI(self.instance.__name__)
        self.itemsCurrentMenu[0] = itemMenu
        try:
            if self.page < math.ceil(self.EController.getCount() / self.per_page):
                itemMenu.addField(">>>", lambda: self.__changePageParams(self.page + 1, self.per_page))
            if self.page > 1:
                itemMenu.addField("<<<", lambda: self.__changePageParams(self.page - 1, self.per_page))
            entities = self.EController.getPaginate(self.page, self.per_page)
            for entity in entities:
                if self.instance.__name__ == "News":
                    itemMenu.addField(f"\"{entity.title}\"     ({entity.date})     *{entity.rating}", lambda id=entity.id: self.__getItem(id))
                else:
                    itemMenu.addField(f"[{entity.id}] {entity.name}", lambda id=entity.id: self.__getItem(id))
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run("Back to Main Menu")

    def __getItem(self, id: int):
        itemMenu = CUI(f"{self.instance.__name__} Menu")
        self.itemsCurrentMenu[1] = itemMenu
        try:
            item = self.EController.getById(id)
            for (key, value) in self.EController.getModelEntityMappedKeys(item).items():
                itemMenu.addField(str(key) + " : " + str(value))

            if self.instance.__name__ == "News":
                itemMenu.addField("Show tags", lambda: self.__getNewsTags(item.id))
            if self.instance.__name__ == "Tag":
                itemMenu.addField("Show topics", lambda: self.__getTagTopics(item.id))

            itemMenu.addField("UPDATE", lambda: self.__update(item))
            itemMenu.addField("DELETE", lambda: self.__delete(item.id))
            itemMenu.addField("Back to Previous Menu", lambda: self.__supportCUIFunc())
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run(False)

    def __add(self):
        try:
            mapped = {}
            self.__createEntityMenu(mapped)
            execStr = ""
            for value in mapped.values():
                if value is None or (isinstance(value, str) and any((char in exec_bad_chars) for char in value)):
                    raise Exception("Invalid entity values")
                if isinstance(value, str):
                    execStr += f"'{value}', "
                else:
                    execStr += f"{value}, "
            exec("self.entity = self.instance(%s)" % execStr[:-1])
            id = self.EController.add(self.entity)
            self.CUI.setError(f"Successfully created new entity by id {id}")
        except Exception as err:
            self.CUI.setError(str(err))

    def __update(self, item):
        self.__createEntityMenu(item)
        self.EController.update(item)
        self.itemsCurrentMenu[1].stop()
        self.__getItem(item.id)

    def __updateTags(self, page: int, menu, nid: int):
        self.tags_page = page
        menu.stop()
        self.__getNewsTags(nid)

    def __updateTopics(self, page: int, menu, tid: int):
        self.tags_page = page
        menu.stop()
        self.__getTagTopics(tid)

    def __updateTitleSearch(self, page: int, menu, title: str):
        self.title_page = page
        menu.stop()
        self.__searchNewsTitle()

    def __updateRatingSearch(self, page: int, menu, min: float, max: float):
        self.title_page = page
        menu.stop()
        self.__searchNewsTitle()

    def __delete(self, id: int):
        self.EController.delete(id)
        self.itemsCurrentMenu[1].stop()
        self.__supportCUIFunc()

    def __searchNewsTitle(self):
        itemMenu = CUI(self.instance.__name__)
        self.itemsCurrentMenu[1] = itemMenu
        try:
            title = str(input("Enter title: "))

            news = self.QController.getNewsByTitleFragment(title)
            if self.title_page < math.ceil(len(news) / self.per_page):
                itemMenu.addField(">>>", lambda: self.__updateTitleSearch(self.title_page + 1, itemMenu, title))
            if self.title_page > 1:
                itemMenu.addField("<<<", lambda: self.__updateTitleSearch(self.title_page - 1, itemMenu, title))
            news = self.QController.getNewsByTitleFragment(title, self.title_page, self.per_page)

            for n in news:
               itemMenu.addField(f"\"{n.title}\"     ({n.date})     *{n.rating}", lambda id=n.id: self.__getItem(id))
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run("Back to Previous Menu")

    def __searchNewsRating(self):
        itemMenu = CUI(self.instance.__name__)
        self.itemsCurrentMenu[1] = itemMenu
        try:
            min = float(input("Enter min rating: "))
            max = float(input("Enter max rating: "))
            if not (isinstance(min, float) and isinstance(max, float) and max >= min and min > 0 and max > 0):
                raise ValueError("Invalid input")

            news = self.QController.getNewsByRatingRange(min, max)
            if self.rating_page < math.ceil(len(news) / self.per_page):
                itemMenu.addField(">>>", lambda: self.__updateRatingSearch(self.rating_page + 1, self.per_page))
            if self.rating_page > 1:
                itemMenu.addField("<<<", lambda: self.__updateRatingSearch(self.rating_page - 1, self.per_page))
            news = self.QController.getNewsByRatingRange(min, max, self.rating_page, self.per_page)

            for n in news:
                itemMenu.addField(f"[{n.id}] \"{n.title}\"     ({n.date})     *{n.rating}", lambda id=n.id: self.__getItem(id))
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run("Back to Previous Menu")

    def __getNewsTags(self, nid: int):
        itemMenu = CUI(self.instance.__name__)
        try:
            tags = self.QController.getAllNewsTags(nid)
            if self.tags_page < math.ceil(len(tags) / self.per_page):
                itemMenu.addField(">>>", lambda: self.__updateTags(self.tags_page + 1, itemMenu, nid))
            if self.tags_page > 1:
                itemMenu.addField("<<<", lambda: self.__updateTags(self.tags_page - 1, itemMenu, nid))
            tags = self.QController.getAllNewsTags(nid, self.tags_page, self.per_page)

            for t in tags:
                itemMenu.addField(f"[{t.id}] {t.name}")
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run("Back to Previous Menu")

    def __getTagTopics(self, tid: int):
        itemMenu = CUI(self.instance.__name__)
        try:
            topics = self.QController.getAllTagTopics(tid)
            if self.topics_page < math.ceil(len(topics) / self.per_page):
                itemMenu.addField(">>>", lambda: self.__updateTopics(self.tags_page + 1, itemMenu, tid))
            if self.topics_page > 1:
                itemMenu.addField("<<<", lambda: self.__updateTopics(self.tags_page - 1, itemMenu, tid))
            topics = self.QController.getAllNewsTags(tid, self.topics_page, self.per_page)

            for t in topics:
                itemMenu.addField(f"[{t.id}] {t.name}")
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run("Back to Previous Menu")

    def __changePageParams(self, page: int, per_page: int):
        self.page = page
        self.per_page = per_page
        self.itemsCurrentMenu[0].stop()
        self.__getItems()

    def __supportCUIFunc(self):
        self.itemsCurrentMenu[1].stop()
        self.__changePageParams(self.page, self.per_page)

    def __supportcreateItemFunc(self, key, value, item):
        try:
            new = input(f"Enter new {key} value: ")
            if isinstance(new, str) and len(new) > 0:
                if new.isdigit():
                    setattr(item, key, int(new))
                else:
                    setattr(item, key, new)
            else:
                raise Exception("Incorrect input")
            self.currentMenu.renameField(f"{key}:        <{value}>", f"{key}:        <{new}>")
        except Exception as err:
            self.currentMenu.setError(str(err))

    def __supportcreateFunc(self, key, mapped):
        try:
            value = input(f"Enter new {key} value: ")
            old = None
            if key in mapped and mapped[key] is not None:
                old = mapped[key]
            if isinstance(value, str) and len(value) > 0:
                if value.isdigit():
                    mapped[key] = int(value)
                else:
                    mapped[key] = value
            else:
                raise Exception("Incorrect input")

            if old is None:
                self.currentMenu.renameField(f"{key}", f"{key}: {value}")
            else:
                self.currentMenu.renameField(f"{key}: {old}", f"{key}: {value}")
        except Exception as err:
            self.currentMenu.setError(str(err))

    def __createEntityMenu(self, *args):
        self.currentMenu = CUI(f"{self.instance.__name__} Creation")
        try:
            if len(args) > 0 and isinstance(args[0], self.instance):
                item = args[0]
                for (key, value) in self.EController.getModelEntityMappedKeys(item).items():
                    self.currentMenu.addField(f"{key}: {value}", lambda key=key, value=value: self.__supportcreateItemFunc(key, value, item))
            elif len(args) > 0 and isinstance(args[0], dict):
                mapped = args[0]
                for key in self.EController.getModelKeys():
                    mapped[key] = None
                    self.currentMenu.addField(f"{key}", lambda key=key: self.__supportcreateFunc(key, mapped))
            else:
                raise Exception("Invalid arguments")
        except Exception as err:
            self.currentMenu.setError(str(err))
        self.currentMenu.run("Save and Return")

    def run(self):
        self.CUI.run()
