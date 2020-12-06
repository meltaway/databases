import sys
sys.path.append('../')
import math
from controllers.topicController import TopicController
from models.topicModel import Topic
from CUI.cui import CUI

class TopicView:
    def __init__(self):
        self.page = 1
        self.per_page = 10
        self.currentMenu = [None, None]

        self.CUI = CUI("Topic Model Menu")
        self.topicController = TopicController()
        self.CUI.addField("Add Topic", lambda: self.__addTopic())
        self.CUI.addField("Generate Rows", lambda: self.__generateRows())
        self.CUI.addField("Topics", lambda: self.__getTopics())

    def run(self):
        self.CUI.run()

    def __getTopics(self):
        topicMenu = CUI("Topic")
        self.currentMenu[0] = topicMenu
        try:
            if self.page < math.ceil(self.topicController.getCount() / self.per_page):
                topicMenu.addField(">>>", lambda: self.__changePageParams(self.page + 1, self.per_page))
            if self.page > 1:
                topicMenu.addField("<<<", lambda: self.__changePageParams(self.page - 1, self.per_page))
            topics = self.topicController.getAll(self.page, self.per_page)
            for topic in topics:
                topicMenu.addField(f"{topic.name} [{topic.id}]", lambda id=topic.id: self.__getTopic(id))

        except Exception as err:
            topicMenu.setError(str(err))
        topicMenu.run("Back to Main Menu")

    def __getTopic(self, id: int):
        topicMenu = CUI("Topic Menu")
        self.currentMenu[1] = topicMenu
        try:
            topic: Topic = self.topicController.getById(id)
            values = topic.getValues().split(',')
            keys = topic.getKeys().split(',')
            for i in range(len(keys)):
                topicMenu.addField(keys[i] + ' : ' + values[i])

            topicMenu.addField("DELETE", lambda: self.__deleteTopic(topic.id))
            topicMenu.addField("UPDATE", lambda: self.__updateTopic(topic.id))
            topicMenu.addField("Back To Previous Menu", lambda: self.__supportCUIFunc())
        except Exception as err:
            topicMenu.setError(str(err))
        topicMenu.run(False)

    def __addTopic(self):
        try:
            result = self.topicController.add()
            if isinstance(result, bool) and not result:
                raise Exception("Incorrect values")
            else:
                self.CUI.setError("New Topic id: " + str(result))
        except Exception as err:
            self.CUI.setError(str(err))

    def __updateTopic(self, id: int):
        self.topicController.update(id)
        self.currentMenu[1].stop()
        self.__getTopic(id)

    def __deleteTopic(self, id: int):
        self.topicController.delete(id)
        self.currentMenu[1].stop()
        self.__supportCUIFunc()

    def __generateRows(self):
        try:
            n = int(input("Enter number of rows to generate: "))
            if not (isinstance(n, int) and n > 0):
                raise Exception("Invalid input")
            self.CUI.setError("Please wait...")
            time = self.topicController.generateRows(n)
            self.CUI.setError(time + " (done)")
        except Exception as error:
            self.CUI.setError(str(error))

    def __changePageParams(self, page: int, per_page: int):
        self.page = page
        self.per_page = per_page
        self.currentMenu[0].stop()
        self.__getTopics()

    def __supportCUIFunc(self):
        self.currentMenu[1].stop()
        self.__changePageParams(self.page, self.per_page)
