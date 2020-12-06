from models.modelmodel import DbModel

class Topic(DbModel):
    def __init__(self):
        self.id = {
            'type': 'number',
            'value': "DEFAULT",
            'not null': False
        }

        self.name = {
            'type': 'string',
            'value': "DEFAULT",
            'not null': False
        }
