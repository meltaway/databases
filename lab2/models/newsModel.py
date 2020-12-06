from models.modelmodel import DbModel

class News(DbModel):
    def __init__(self):
        self.id = {
            'type': 'number',
            'value': "DEFAULT",
            'not null': False
        }

        self.date = {
            'type': 'date',
            'value': None
        }

        self.title = {
            'type': 'string',
            'value': None
        }

        self.category = {
            'type': 'string',
            'value': None
        }

        self.description = {
            'type': 'string',
            'value': None,
            'not null': False
        }

        self.rating = {
            'type': 'float',
            'value': None
        }
