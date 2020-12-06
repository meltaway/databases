from database import *
from views.entityView import EntityView
from CUI.cui import CUI
from models.newsModel import News
from models.tagModel import Tag
from models.topicModel import Topic

# recreate_database()

cui = CUI("Main Menu")
cui.addField("News", lambda: EntityView(News).run())
cui.addField("Tags", lambda: EntityView(Tag).run())
cui.addField("Topics", lambda: EntityView(Topic).run())
cui.run()

session.close()