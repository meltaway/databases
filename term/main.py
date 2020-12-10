from database import *
from views.entityView import EntityView
from CUI.cui import CUI
from models.newsModel import News
from models.tagModel import Tag
from models.topicModel import Topic
from models.ratingsModel import Rating
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import func

#recreate_database()

# cui = CUI("Main Menu")
# cui.addField("News", lambda: EntityView(News).run())
# cui.addField("Tags", lambda: EntityView(Tag).run())
# cui.addField("Topics", lambda: EntityView(Topic).run())
# cui.run()
#
# session.close()

ratings = session.query(Rating.rating, Rating.date).where(News.id == 1).order_by(Rating.date).offset(3).all()

listed = list(zip(*ratings))
ts = pd.Series(np.array(listed[0]), index=listed[1])
ts = ts.cumsum()
# ts.plot()

plt.plot(ts)
plt.show()