import csv
import os
import json
import time
from models.newsModel import News
from models.tagModel import Tag
from models.topicModel import Topic
from models.ratingsModel import Rating
from controllers.entityController import EntityController
from database import session


class ParseController(object):
    def __init__(self):
        self.filePath = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath('__file__')), './data/news.tsv')))
        self.parsed = []
        self.tagController = EntityController(Tag)
        self.topicController = EntityController(Topic)

    def parseDataset(self):
        try:
            start = time.time()
            file = open(str(self.filePath), encoding="utf8")
            rd = csv.reader(file, delimiter="\t", quotechar='"')
            rowsNum = 0
            for row in rd:
                rowsNum += 1

            file = open(str(self.filePath), encoding="utf8")
            rd = csv.reader(file, delimiter="\t", quotechar='"')

            # tag1 tag2 title description topics(json)
            for row in rd:
                tmp = [row[1].replace('\'', '`').replace('):', ')').replace('/:', '/').replace(' :', ''),
                       row[2].replace('\'', '`').replace('):', ')').replace('/:', '/').replace(' :', ''),
                       row[3].replace('\'', '`').replace('):', ')').replace('/:', '/').replace(' :', ''),
                       row[4].replace('\'', '`').replace('):', ')').replace('/:', '/').replace(' :', ''),
                       row[7].replace('\'', '`').replace('):', ')').replace('/:', '/').replace(' :', '')]
                self.parsed.append(tmp)

            i = 0
            while i < rowsNum:
                array = json.loads(str(self.parsed[i][4]))
                items = []
                for obj in array:
                    items.append(str(obj['Label']).replace('\'', '`'))
                self.parsed[i].append(items)
                i += 1

            #add parsed news
            for item in self.parsed:
                #check if already exists
                tagrow = session.query(Tag.id).where(Tag.name == item[0]).first()
                tag_id = 0
                if tagrow:
                    tag_id = tagrow.id
                else:
                    tag = Tag(item[0])
                    tag_id = self.tagController.add(tag)

                newsrow = session.query(News.id).where(News.title == item[2]).first()
                news_id = 0
                if newsrow:
                    news_id = newsrow.id
                else:
                    if not item[3]:
                        session.execute(f"INSERT INTO news (date, title, category, description, rating) "
                                        f"VALUES (generatedate()::date, '{item[2]}', '{item[1]}', generatestring(100) , generaterating())")
                    else:
                        session.execute(f"INSERT INTO news (date, title, category, description, rating) "
                                        f"VALUES (generatedate()::date, '{item[2]}', '{item[1]}', '{item[3]}', generaterating())")
                    news_id = session.query(News.id).where(News.title == item[2]).first().id
                    session.execute(f"INSERT INTO news_tags (tag_id, news_id) VALUES ({tag_id}, {news_id})")
                    session.commit()

                for t in item[5]:
                    topicrow = session.query(Topic.id).where(Topic.name == str(t)).first()
                    topic_id = 0
                    if topicrow:
                        topic_id = topicrow.id
                    else:
                        topic = Topic(str(t), tag_id)
                        topic_id = self.topicController.add(topic)
            end = time.time()
            return str(end - start)[:9] + 's'
        except Exception as err:
            raise FileNotFoundError(err)