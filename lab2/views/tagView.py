import sys
sys.path.append('../')
import math
from controllers.tagController import TagController
from models.tagModel import Tag
from CUI.cui import CUI

class TagView:
    def __init__(self):
        self.page = 1
        self.per_page = 10
        self.currentMenu = [None, None]

        self.CUI = CUI("Tag Model Menu")
        self.tagController = TagController()
        self.CUI.addField("Add Tag", lambda: self.__addTag())
        self.CUI.addField("Generate Rows", lambda: self.__generateRows())
        self.CUI.addField("Tags", lambda: self.__getTags())

    def run(self):
        self.CUI.run()

    def __getTags(self):
        tagMenu = CUI("Tag")
        self.currentMenu[0] = tagMenu
        try:
            if self.page < math.ceil(self.tagController.getCount() / self.per_page):
                tagMenu.addField(">>>", lambda: self.__changePageParams(self.page + 1, self.per_page))
            if self.page > 1:
                tagMenu.addField("<<<", lambda: self.__changePageParams(self.page - 1, self.per_page))
            tags = self.tagController.getAll(self.page, self.per_page)
            for tag in tags:
                tagMenu.addField(f"{tag.name} [{tag.id}]", lambda id=tag.id: self.__getTag(id))

        except Exception as err:
            tagMenu.setError(str(err))
        tagMenu.run("Back to Main Menu")

    def __getTag(self, id: int):
        tagMenu = CUI("Tag Menu")
        self.currentMenu[1] = tagMenu
        try:
            tag: Tag = self.tagController.getById(id)
            values = tag.getValues().split(',')
            keys = tag.getKeys().split(',')
            for i in range(len(keys)):
                tagMenu.addField(keys[i] + ' : ' + values[i])

            tagMenu.addField("DELETE", lambda: self.__deleteTag(tag.id))
            tagMenu.addField("UPDATE", lambda: self.__updateTag(tag.id))
            tagMenu.addField("Back To Previous Menu", lambda: self.__supportCUIFunc())
        except Exception as err:
            tagMenu.setError(str(err))
        tagMenu.run(False)

    def __addTag(self):
        try:
            result = self.tagController.add()
            if isinstance(result, bool) and not result:
                raise Exception("Incorrect values")
            else:
                self.CUI.setError("New Tag id: " + str(result))
        except Exception as err:
            self.CUI.setError(str(err))

    def __updateTag(self, id: int):
        self.tagController.update(id)
        self.currentMenu[1].stop()
        self.__getTag(id)

    def __deleteTag(self, id: int):
        self.tagController.delete(id)
        self.currentMenu[1].stop()
        self.__supportCUIFunc()

    def __generateRows(self):
        try:
            n = int(input("Enter number of rows to generate: "))
            if not (isinstance(n, int) and n > 0):
                raise Exception("Invalid input")
            self.CUI.setError("Please wait...")
            time = self.tagController.generateRows(n)
            self.CUI.setError(time + " (done)")
        except Exception as error:
            self.CUI.setError(str(error))

    def __changePageParams(self, page: int, per_page: int):
        self.page = page
        self.per_page = per_page
        self.currentMenu[0].stop()
        self.__getTags()

    def __supportCUIFunc(self):
        self.currentMenu[1].stop()
        self.__changePageParams(self.page, self.per_page)
