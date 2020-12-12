from sqlalchemy import func, select, update
from sqlalchemy.orm.attributes import InstrumentedAttribute
from database import session
from models.ratingsModel import Rating
from models.newsModel import News
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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
