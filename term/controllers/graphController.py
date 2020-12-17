from database import session
from models.ratingsModel import Rating
from models.newsModel import News
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math


class GraphController(object):
    def getRatingsGraph(self, nid: int):
        ratings = session.query(Rating.rating).where(Rating.news_id == nid).order_by(Rating.date).all()
        count = len(ratings)
        title = session.query(News.title).where(News.id == nid).one()
        graphTitle = f"Ratings for \"{title[0]}\""

        listed = list(zip(*ratings))
        ts = np.array(listed[0])
        avg = np.mean(ts)

        if ratings[count - 1].rating - ratings[0].rating > avg:
            graphTitle += " (it's a trend!)"

        delta = 0.2

        fig = plt.figure()
        axes = fig.add_subplot(111)
        axes.set_title(graphTitle)
        axes.set_xlabel("Count")
        axes.set_ylabel("Value")
        axes.axhline(avg, label="Trend boundary", linestyle="--", color="red")
        axes.set_ylim(np.min(ts) - delta, np.max(ts) + delta)

        axes.plot(np.arange(1, count + 1).astype(str), ts, linestyle="-", color="black", label="Rating")
        axes.legend()
        plt.show()

    def getTopTagsGraph(self):
        results = session.execute("SELECT name, avg FROM "
                                  "(SELECT tag_id, avg(rating) FROM news_tags "
                                  "INNER JOIN news n ON n.id = news_tags.news_id "
                                  "GROUP BY tag_id "
                                  "LIMIT 10) AS t "
                                  "INNER JOIN tags ON tags.id = t.tag_id "
                                  "ORDER BY avg DESC").all()
        listed = list(zip(*results))
        series = pd.Series(np.array(listed[1]), index=listed[0], name='')
        series.plot.pie(figsize=(9, 7), title="Top 10 Rated Tags:")
        plt.show()

    def getTrendingTags(self):
        results = session.execute("SELECT name, (avg / count) AS k FROM "
                                  "(SELECT tag_id, count(tag_id) FROM news_tags "
                                  "GROUP BY tag_id) AS t1 "
                                  "INNER JOIN "
                                  "(SELECT tag_id, name, avg FROM "
                                  "(SELECT tag_id, avg(rating) FROM news_tags "
                                  "INNER JOIN news n ON n.id = news_tags.news_id "
                                  "GROUP BY tag_id) AS t "
                                  "INNER JOIN tags ON tags.id = t.tag_id) AS t2 "
                                  "ON t1.tag_id = t2.tag_id "
                                  "ORDER BY k DESC "
                                  "LIMIT 10").all()
        listed = list(zip(*results))
        k = np.array([math.log10(item * 1000) for item in listed[1]])
        avg = k.mean()
        df = pd.DataFrame({'coefficient': k}, index=listed[0])
        df.plot.bar(figsize=(9, 7), title="Top 10 Tags By Trend Coefficient")
        plt.axhline(avg, label="Trend boundary", linestyle="--", color="red")
        plt.legend()
        plt.show()
