from django.db import models
import timezone


class Entry(models.Model):
    date_on_timeline = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)

    schema = models.CharField(max_length=100)
    title = models.TextField()
    description = models.TextField()
    extra_attributes = models.JSONField()

    def get_schema(self):
        raise NotImplementedError

    def get_object(self):
        return {
            'title': self.title,
            'description': self.description,
            'schema': self.get_schema(),
        } + self.extra_attributes


class Text(Entry):
    class Meta:
        proxy = True

    def get_schema(self):
        return 'text'


class Location(Entry):
    class Meta:
        proxy = True

    def get_schema(self):
        return 'geo.point'


class Markdown(Text):
    class Meta:
        proxy = True

    def get_schema(self):
        return super().get_schema() + '.markdown'

    def get_object(self):
        obj = super().get_object()
        obj.update({
            'htmlDescription': obj['description'],
        })
        return obj


class File(Entry):
    class Meta:
        proxy = True

    def get_schema(self):
        return 'file'


class Image(File):
    class Meta:
        proxy = True

    def get_schema(self):
        return super().get_schema() + '.image'


class Video(File):
    class Meta:
        proxy = True

    def get_schema(self):
        return super().get_schema() + '.video'