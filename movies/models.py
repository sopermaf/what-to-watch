from django.db import models
from marshmallow import Schema, fields, pre_load


class Genre(models.Model):
    name = models.CharField()


class TitleType(models.Model):
    name = models.CharField()


class WatchItem(models.Model):
    imdb_id = models.CharField(unique=True)
    average_rating = models.FloatField(db_index=True)
    num_votes = models.PositiveBigIntegerField()
    title_type = models.ForeignKey(TitleType)
    primary_title = models.CharField()
    original_title = models.CharField()
    is_adult = models.BooleanField()
    start_year = models.PositiveIntegerField(db_index=True)
    end_year = models.PositiveIntegerField(null=True)
    runtime_minutes = models.IntegerField()
    genres = models.ManyToManyRel(Genre, null=True, related_name="watch_items")

    @classmethod
    def create_watch_item(cls, watch_item):
        # create the watch item without save
        genres = [
            Genre.objects.get_or_create(name=genre)
            for genre in watch_item.pop("genres")
        ]
        title_type = TitleType.get_or_create(name=watch_item.pop("title_type"))

        # TODO: how to handle updating?
        new_watch_item = WatchItem(**watch_item, title_type=title_type)
        new_watch_item.save()

        new_watch_item.genres.add(*genres)
        new_watch_item.save()


class WatchItemSchema(Schema):
    imdb_id = fields.String(data_key="tconst")
    average_rating = fields.Float(data_key="averageRating")
    num_votes = fields.Integer(data_key="numVotes")
    title_type = fields.String(data_key="titleType")
    primary_title = fields.String(data_key="primaryTitle")
    original_title = fields.String(data_key="originalTitle")
    is_adult = fields.Boolean(data_key="isAdult")
    start_year = fields.String(data_key="startYear")
    end_year = fields.String(data_key="endYear", allow_none=True)
    runtime_minutes = fields.String(data_key="runtimeMinutes")
    genres = fields.List(fields.String)

    @pre_load
    def clean_values(self, data, **_):
        # remove `\N` for null
        for k, v in data.items():
            if v == r"\N":
                data[k] = None

        # split genre
        try:
            genres = data["genres"].split(",")
        except AttributeError:
            genres = []
        finally:
            data["genres"] = genres if any(genres) else []

        return data
