import math
from controllers.entityController import ModelController
from CUI.cui import CUI

exec_bad_chars = set('{}()[],;+*\/')

class EntityView:
    def __init__(self, instance):
        self.instance = instance
        self.page = 1
        self.itemsCurrentMenu = [None, None]
        self.per_page = 10
        self.CUI = CUI(f"{self.instance.__name__} Menu")
        self.Controller = ModelController(instance)

        self.CUI.addField(f"Add {self.instance.__name__}", lambda: self.__add())
        self.CUI.addField(f"{self.instance.__name__}", lambda: self.__getItems())
        self.CUI.addField("Generate rows", lambda: self.__generateRows())

    def __generateRows(self):
        items = CUI(self.instance.__name__)
        self.itemsCurrentMenu[0] = items

        try:
            n = int(input("Enter number of rows to generate: "))
            if not (isinstance(n, int) and n > 0):
                raise Exception("Invalid input")

            if self.instance.__name__ == "News":

        except Exception as err:
            items.setError(str(err))
        items.run("Back to Main Menu")

    def __getItems(self):
        items = CUI(self.instance.__name__)
        self.itemsCurrentMenu[0] = items
        try:
            if self.page < math.ceil(self.Controller.getCount() / self.per_page):
                items.addField(">>>", lambda: self.__changePageParams(self.page + 1, self.per_page))
            if self.page > 1:
                items.addField("<<<", lambda: self.__changePageParams(self.page - 1, self.per_page))
            entities = self.Controller.getPaginate(self.page, self.per_page)
            for entity in entities:
                if self.instance.__name__ == "News":
                    items.addField(f"\"{entity.title}\"     ({entity.date})     *{entity.rating}", lambda id=entity.id: self.__getItem(id))
                else:
                    items.addField(f"[{entity.id}] {entity.name}", lambda id=entity.id: self.__getItem(id))

        except Exception as err:
            items.setError(str(err))
        items.run("Back to Main Menu")

    def __getItem(self, id: int):
        itemMenu = CUI(f"{self.instance.__name__} Menu")
        self.itemsCurrentMenu[1] = itemMenu
        try:
            item = self.Controller.getById(id)
            for (key, value) in self.Controller.getModelEntityMappedKeys(item).items():
                itemMenu.addField(str(key) + " : " + str(value))

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
            id = self.Controller.add(self.entity)
            self.CUI.setError(f"Successfully created new entity by id {id}")
        except Exception as err:
            self.CUI.setError(str(err))

    def __update(self, item):
        self.__createEntityMenu(item)
        self.Controller.update(item)
        self.itemsCurrentMenu[1].stop()
        self.__getItem(item.id)

    def __delete(self, id: int):
        self.Controller.delete(id)
        self.itemsCurrentMenu[1].stop()
        self.__supportCUIFunc()

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
                for (key, value) in self.Controller.getModelEntityMappedKeys(item).items():
                    self.currentMenu.addField(f"{key}: {value}", lambda key=key, value=value: self.__supportcreateItemFunc(key, value, item))
            elif len(args) > 0 and isinstance(args[0], dict):
                mapped = args[0]
                for key in self.Controller.getModelKeys():
                    mapped[key] = None
                    self.currentMenu.addField(f"{key}", lambda key=key: self.__supportcreateFunc(key, mapped))
            else:
                raise Exception("Invalid arguments")
        except Exception as err:
            self.currentMenu.setError(str(err))
        self.currentMenu.run("Save and Return")

    def run(self):
        self.CUI.run()
