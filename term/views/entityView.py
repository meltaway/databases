import math
import datetime
from controllers.entityController import EntityController
from controllers.queryController import QueryController
from controllers.randomController import RandomController
from controllers.graphController import GraphController
from controllers.parseController import ParseController
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
        self.date_page = 1
        self.per_page = 10

        self.title = None
        self.minr = None
        self.maxr = None
        self.mind = None
        self.maxd = None

        self.itemsCurrentMenu = [None, None]

        self.CUI = CUI(f"{self.instance.__name__} Menu")
        self.EController = EntityController(instance)
        self.QController = QueryController(instance)
        self.RController = RandomController()
        self.GController = GraphController()
        self.PController = ParseController()

        self.CUI.addField(f"Add {self.instance.__name__}", lambda: self.__add())
        self.CUI.addField(f"{self.instance.__name__}", lambda: self.__getItems())
        self.CUI.addField("Generate rows", lambda: self.__generateRows())

        if self.instance.__name__ == "News":
            self.CUI.addField("Parse MIND dataset", lambda: self.__parseDataset())
            self.CUI.addField("Search by title fragment", lambda: self.__searchNewsTitle())
            self.CUI.addField("Search by rating range", lambda: self.__searchNewsRating())
            self.CUI.addField("Search by date range", lambda: self.__searchNewsDate())


    def __generateRows(self):
        itemMenu = CUI(self.instance.__name__)
        self.itemsCurrentMenu[1] = itemMenu
        try:
            n = int(input("Enter number of rows to generate: "))
            if not (isinstance(n, int) and n > 0):
                raise Exception("Invalid input")

            if self.instance.__name__ == "News":
                if not self.RController.generateNews(n):
                    raise Exception("Could not generate news!")
            if self.instance.__name__ == "Tag":
                if not self.RController.generateTags(n):
                    raise Exception("Could not generate tags!")
            if self.instance.__name__ == "Topic":
                if not self.RController.generateTopics(n):
                    raise Exception("Could not generate topics!")
        except Exception as err:
            itemMenu.setError(str(err))

    def __parseDataset(self):
        itemMenu = CUI(self.instance.__name__)
        self.itemsCurrentMenu[1] = itemMenu
        try:
            itemMenu.setError("Please wait, this may take a long time...")
            time = self.PController.parseDataset()
            itemMenu.setError(time + " (done)")
            itemMenu.deleteField("Parse MIND dataset")
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
            entities = self.EController.getPaginated(self.page, self.per_page)
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
            for (key, value) in self.EController.getEntityMappedKeys(item).items():
                itemMenu.addField(str(key) + " : " + str(value))

            if self.instance.__name__ == "News":
                itemMenu.addField("Show Tags", lambda: self.__getNewsTags(item.id))
                itemMenu.addField("Show Ratings Graph", lambda: self.__getRatingsGraph(item.id))
            if self.instance.__name__ == "Tag":
                itemMenu.addField("Show Topics", lambda: self.__getTagTopics(item.id))

            itemMenu.addField("UPDATE", lambda: self.__update(item))
            itemMenu.addField("DELETE", lambda: self.__delete(item.id))
            itemMenu.addField("Back to Previous Menu", lambda: self.__supportCUI())
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run(False)

    def __add(self):
        try:
            mapped = {}
            self.__addMenu(mapped)
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
        self.__addMenu(item)
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

    def __updateTitleSearch(self, page: int, menu):
        self.title_page = page
        menu.stop()
        self.__searchNewsTitle()

    def __updateRatingSearch(self, page: int, menu):
        self.rating_page = page
        menu.stop()
        self.__searchNewsRating()

    def __updateDateSearch(self, page: int, menu):
        self.date_page = page
        menu.stop()
        self.__searchNewsDate()

    def __delete(self, id: int):
        self.EController.delete(id)
        self.itemsCurrentMenu[1].stop()
        self.__supportCUI()

    def __searchNewsTitle(self):
        itemMenu = CUI(self.instance.__name__)
        self.itemsCurrentMenu[1] = itemMenu
        try:
            if self.title is None:
                self.title = str(input("Enter title: "))

            news = self.QController.getNewsByTitleFragment(self.title)
            if self.title_page < math.ceil(len(news) / self.per_page):
                itemMenu.addField(">>>", lambda: self.__updateTitleSearch(self.title_page + 1, itemMenu))
            if self.title_page > 1:
                itemMenu.addField("<<<", lambda: self.__updateTitleSearch(self.title_page - 1, itemMenu))
            news = self.QController.getNewsByTitleFragment(self.title, self.title_page, self.per_page)

            for n in news:
               itemMenu.addField(f"\"{n.title}\"     ({n.date})     *{n.rating}", lambda id=n.id: self.__getItem(id))
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run("Back to Previous Menu")
        self.title_page = 1
        self.title = None

    def __searchNewsRating(self):
        itemMenu = CUI(self.instance.__name__)
        self.itemsCurrentMenu[1] = itemMenu
        try:
            if self.minr is None and self.maxr is None:
                self.minr = float(input("Enter min rating: "))
                self.maxr = float(input("Enter max rating: "))
            if not (isinstance(self.minr, float) and isinstance(self.maxr, float) and self.maxr >= self.minr and self.minr > 0 and self.maxr > 0):
                raise ValueError("Invalid input")

            news = self.QController.getNewsByRatingRange(self.minr, self.maxr)
            if self.rating_page < math.ceil(len(news) / self.per_page):
                itemMenu.addField(">>>", lambda: self.__updateRatingSearch(self.rating_page + 1, itemMenu))
            if self.rating_page > 1:
                itemMenu.addField("<<<", lambda: self.__updateRatingSearch(self.rating_page - 1, itemMenu))
            news = self.QController.getNewsByRatingRange(self.minr, self.maxr, self.rating_page, self.per_page)

            for n in news:
                itemMenu.addField(f"\"{n.title}\"     ({n.date})     *{n.rating}", lambda id=n.id: self.__getItem(id))
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run("Back to Previous Menu")
        self.rating_page = 1
        self.minr = None
        self.maxr = None

    def __searchNewsDate(self):
        itemMenu = CUI(self.instance.__name__)
        self.itemsCurrentMenu[1] = itemMenu
        try:
            if self.mind is None and self.maxd is None:
                self.mind = str(input("Enter starting date (inclusive) [YYYY-MM-DD]: "))
                self.maxd = str(input("Enter endind date (inclusive) [YYYY-MM-DD]: "))
            if not (isinstance(self.mind, str) and isinstance(self.maxd, str) and self.maxd >= self.mind):
                raise ValueError("Invalid input")

            date1 = None
            date2 = None
            try:
                date1 = datetime.datetime(int(self.mind.split('-')[0]), int(self.mind.split('-')[1]),
                                        int(self.mind.split('-')[2]))
                date2 = datetime.datetime(int(self.maxd.split('-')[0]), int(self.maxd.split('-')[1]),
                                        int(self.maxd.split('-')[2]))
            except Exception:
                raise ValueError("Invalid input")

            news = self.QController.getNewsByDateRange(date1, date2)
            if self.date_page < math.ceil(len(news) / self.per_page):
                itemMenu.addField(">>>", lambda: self.__updateDateSearch(self.date_page + 1, itemMenu))
            if self.date_page > 1:
                itemMenu.addField("<<<", lambda: self.__updateDateSearch(self.date_page - 1, itemMenu))
            news = self.QController.getNewsByDateRange(date1, date2, self.date_page, self.per_page)

            for n in news:
                itemMenu.addField(f"\"{n.title}\"     ({n.date})     *{n.rating}", lambda id=n.id: self.__getItem(id))
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run("Back to Previous Menu")
        self.date_page = 1
        self.mind = None
        self.maxd = None

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
                itemMenu.addField(">>>", lambda: self.__updateTopics(self.topics_page + 1, itemMenu, tid))
            if self.topics_page > 1:
                itemMenu.addField("<<<", lambda: self.__updateTopics(self.topics_page - 1, itemMenu, tid))
            topics = self.QController.getAllTagTopics(tid, self.topics_page, self.per_page)

            for t in topics:
                itemMenu.addField(f"[{t.id}] {t.name}")
        except Exception as err:
            itemMenu.setError(str(err))
        itemMenu.run("Back to Previous Menu")

    def __getRatingsGraph(self, nid: int):
        self.GController.getRatingsGraph(nid)

    def __changePageParams(self, page: int, per_page: int):
        self.page = page
        self.per_page = per_page
        self.itemsCurrentMenu[0].stop()
        self.__getItems()

    def __supportCUI(self):
        self.itemsCurrentMenu[1].stop()
        self.__changePageParams(self.page, self.per_page)

    def __supportAddCUI(self, key, value, item):
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

    def __supportAdd(self, key, mapped):
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

    def __addMenu(self, *args):
        self.currentMenu = CUI(f"{self.instance.__name__} Creation")
        try:
            if len(args) > 0 and isinstance(args[0], self.instance):
                item = args[0]
                for (key, value) in self.EController.getEntityMappedKeys(item).items():
                    self.currentMenu.addField(f"{key}: {value}", lambda key=key, value=value: self.__supportAddCUI(key, value, item))
            elif len(args) > 0 and isinstance(args[0], dict):
                mapped = args[0]
                for key in self.EController.getModelKeys():
                    mapped[key] = None
                    self.currentMenu.addField(f"{key}", lambda key=key: self.__supportAdd(key, mapped))
            else:
                raise Exception("Invalid arguments")
        except Exception as err:
            self.currentMenu.setError(str(err))
        self.currentMenu.run("Save and Return")

    def run(self):
        self.CUI.run()
