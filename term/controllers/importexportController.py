from database import session
from models.ratingsModel import Rating
from models.newsModel import News
from models.topicModel import Topic
from models.tagModel import Tag
from controllers.entityController import EntityController
import pandas as pd
import csv
import os
import time

class ImportExportController(object):
    def __init__(self):
        self.entity = ""
        self.filePath = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath('__file__')),
                                                                      f'./data/{self.entity}.csv')))
        self.newsController = EntityController(News)
        self.tagController = EntityController(Tag)
        self.topicController = EntityController(Topic)
        self.ratingController = EntityController(Rating)

    def setFilePath(self, entity: str):
        self.filePath = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath('__file__')),
                                                                      f'./data/{entity}.csv')))

    def importNews(self):
        try:
            start = time.time()
            self.setFilePath('news')
            frame = pd.read_csv(self.filePath)
            for i, row in frame.iterrows():
                newsrow = session.query(News.id).where(News.title == row['title']).first()
                news_id = 0
                if newsrow:
                    news_id = newsrow.id
                else:
                    news = News(row['date'], row['title'], row['category'], row['description'], float(row['rating']))
                    news_id = self.newsController.add(news)
            end = time.time()
            return str(end - start)[:9] + 's'
        except Exception as err:
            raise FileNotFoundError(err)

    def importTags(self):
        try:
            start = time.time()
            self.setFilePath('tags')
            frame = pd.read_csv(self.filePath)
            for i, row in frame.iterrows():
                tagrow = session.query(Tag.id).where(Tag.name == row['name']).first()
                tag_id = 0
                if tagrow:
                    tag_id = tagrow.id
                else:
                    tag = Tag(row['name'])
                    tag_id = self.tagController.add(tag)
            end = time.time()
            return str(end - start)[:9] + 's'
        except Exception as err:
            raise FileNotFoundError(err)

    def importTopics(self):
        try:
            start = time.time()
            self.setFilePath('topics')
            frame = pd.read_csv(self.filePath)
            for i, row in frame.iterrows():
                topicrow = session.query(Topic.id).where(Topic.name == row['name']).first()
                topic_id = 0
                if topicrow:
                    topic_id = topicrow.id
                else:
                    topic = Topic(row['name'], int(row['tag_id']))
                    topic_id = self.topicController.add(topic)
            end = time.time()
            return str(end - start)[:9] + 's'
        except Exception as err:
            raise FileNotFoundError(err)

    def importRatings(self):
        try:
            self.setFilePath('ratings')
            frame = pd.read_csv(self.filePath)
            for i, row in frame.iterrows():
                ratingrow = session.query(Rating.id).where(Rating.news_id == row['news_id']).first()
                rating_id = 0
                if ratingrow:
                    rating_id = ratingrow.id
                else:
                    rating = Rating(int(row['news_id']), row['date'], float(row['rating']))
                    rating_id = self.ratingController.add(rating)
        except Exception as err:
            raise FileNotFoundError(err)

    def importLinks(self):
        try:
            self.setFilePath('links')
            frame = pd.read_csv(self.filePath)
            for i, row in frame.iterrows():
                linkrow = session.execute(f"SELECT * FROM news_tags "
                                          f"WHERE news_id = {row['news_id']} AND tag_id = {row['tag_id']}").first()
                news_id = 0
                if linkrow:
                    news_id = linkrow.news_id
                else:
                    session.execute(f"INSERT INTO news_tags (tag_id, news_id) "
                                    f"VALUES ({row['tag_id']}, {row['news_id']})")
                    session.commit()
        except Exception as err:
            raise FileNotFoundError(err)

    def exportNews(self):
        try:
            start = time.time()
            news = session.query(News).order_by(News.id.asc()).all()
            self.setFilePath('news')
            file = open(self.filePath, 'w', newline='')
            with file:
                header = ['date', 'title', 'category', 'description', 'rating']
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                for row in news:
                    writer.writerow({'date': row.date, 'title': row.title, 'category': row.category,
                                     'description': row.description, 'rating': row.rating})
            end = time.time()
            return str(end - start)[:9] + 's'
        except Exception as err:
            raise ValueError(err)

    def exportTags(self):
        try:
            start = time.time()
            tags = session.query(Tag).order_by(Tag.id.asc()).all()
            self.setFilePath('tags')
            file = open(self.filePath, 'w', newline='')
            with file:
                header = ['name']
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                for row in tags:
                    writer.writerow({'name': row.name})
            end = time.time()
            return str(end - start)[:9] + 's'
        except Exception as err:
            raise ValueError(err)

    def exportTopics(self):
        try:
            start = time.time()
            topics = session.query(Topic).order_by(Topic.id.asc()).all()
            self.setFilePath('topics')
            file = open(self.filePath, 'w', newline='')
            with file:
                header = ['name', 'tag_id']
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                for row in topics:
                    writer.writerow({'name': row.name, 'tag_id': row.tag_id})
            end = time.time()
            return str(end - start)[:9] + 's'
        except Exception as err:
            raise ValueError(err)

    def exportRatings(self):
        try:
            start = time.time()
            ratings = session.query(Rating).order_by(Rating.id.asc()).all()
            self.setFilePath('ratings')
            file = open(self.filePath, 'w', newline='')
            with file:
                header = ['news_id', 'date', 'rating']
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                for row in ratings:
                    writer.writerow({'news_id': row.news_id, 'date': row.date, 'rating': row.rating})
            end = time.time()
            return str(end - start)[:9] + 's'
        except Exception as err:
            raise ValueError(err)

    def exportLinks(self):
        try:
            start = time.time()
            links = session.execute("SELECT * FROM news_tags ORDER BY news_id").all()
            self.setFilePath('links')
            file = open(self.filePath, 'w', newline='')
            with file:
                header = ['tag_id', 'news_id']
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                for row in links:
                    writer.writerow({'tag_id': row.tag_id, 'news_id': row.news_id})
            end = time.time()
            return str(end - start)[:9] + 's'
        except Exception as err:
            raise ValueError(err)
