from database import *
from views.entityView import EntityView
from CUI.cui import CUI
from models.newsModel import News
from models.tagModel import Tag
from models.topicModel import Topic
import numpy

# recreate_database()

cui = CUI("Main Menu")
cui.addField("News", lambda: EntityView(News).run())
cui.addField("Tags", lambda: EntityView(Tag).run())
cui.addField("Topics", lambda: EntityView(Topic).run())
cui.run()

session.close()


# items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# page = 0
# per_page = 3
#
# page -= 1
# if page * per_page + per_page > len(items) - 1:
#     newitems = items[page * per_page:]
# else:
#     newitems = items[page * per_page: (page + 1) * per_page]
#
# print(newitems)
