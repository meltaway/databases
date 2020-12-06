from views.newsView import NewsView
from views.tagView import TagView
from views.topicView import TopicView
from views.queryView import QueryView
from CUI.cui import CUI

main = CUI()
main.addField("News", lambda: NewsView().run())
main.addField("Tags", lambda: TagView().run())
main.addField("Topics", lambda: TopicView().run())
main.addField("Search Queries", lambda: QueryView().run())
main.run()
