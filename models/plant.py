from mongoengine import Document, StringField, BooleanField, FloatField, EmbeddedDocument, DateTimeField, ListField, \
    EmbeddedDocumentField


class SensorValue(EmbeddedDocument):
    value = FloatField(required=True)
    timestamp = DateTimeField(required=True)


class Plant(Document):
    name = StringField(required=True, unique=True)
    description = StringField(required=True)
    key = StringField(required=True, unique=True)
    state = BooleanField(required=True, default=False)
    temperatures = ListField(EmbeddedDocumentField(SensorValue))
    humidities = ListField(EmbeddedDocumentField(SensorValue))
    moistures = ListField(EmbeddedDocumentField(SensorValue))
    light_values = ListField(EmbeddedDocumentField(SensorValue))

    meta = {
        'collection': 'plants',
        'indexes': [{'fields': ['name'], 'unique': True}]
    }

