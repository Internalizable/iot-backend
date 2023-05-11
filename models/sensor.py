from mongoengine import Document, StringField, FloatField, EmbeddedDocument, DateTimeField, ListField, \
    EmbeddedDocumentField


class SensorValue(EmbeddedDocument):
    value = FloatField(required=True)
    timestamp = DateTimeField(required=True)

class Sensor(Document):
    name = StringField(required=True, unique=True)
    description = StringField(required=True)
    key = StringField(required=True)
    temperatures = ListField(EmbeddedDocumentField(SensorValue))
    humidities = ListField(EmbeddedDocumentField(SensorValue))
    moistures = ListField(EmbeddedDocumentField(SensorValue))
    light_values = ListField(EmbeddedDocumentField(SensorValue))

    meta = {
        'collection': 'sensors',
        'indexes': [{'fields': ['name'], 'unique': True}]
    }
