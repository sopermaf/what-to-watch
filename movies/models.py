from django.db import models
from marshmallow import Schema, fields, pre_load


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TitleType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class WatchItem(models.Model):
    imdb_id = models.CharField(unique=True, max_length=30)
    average_rating = models.FloatField(db_index=True)
    num_votes = models.PositiveBigIntegerField()
    title_type = models.ForeignKey(TitleType, on_delete=models.CASCADE)
    primary_title = models.CharField(max_length=100)
    original_title = models.CharField(max_length=100)
    is_adult = models.BooleanField(default=False)
    start_year = models.PositiveIntegerField(db_index=True, null=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    runtime_minutes = models.IntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name="watch_items")

    def __str__(self) -> str:
        return f"WatchItem({self.imdb_id=}, {self.average_rating=})"

    @property
    def imdb_link(self) -> str:
        return f"https://www.imdb.com/title/{self.imdb_id}/"

    @classmethod
    def create_watch_item(cls, watch_item):
        # create the watch item without save
        genres = [
            Genre.objects.get_or_create(name=genre)
            for genre in watch_item.pop("genres")
        ]
        title_type, _ = TitleType.objects.get_or_create(
            name=watch_item.pop("title_type")
        )

        # TODO: how to handle updating?
        new_watch_item = WatchItem(**watch_item, title_type=title_type)
        new_watch_item.save()

        new_watch_item.genres.add(*(g for g, _ in genres))
        new_watch_item.save()


class WatchItemSchema(Schema):
    imdb_id = fields.String(data_key="tconst")
    average_rating = fields.Float(data_key="averageRating")
    num_votes = fields.Number(data_key="numVotes")
    title_type = fields.String(data_key="titleType")
    primary_title = fields.String(data_key="primaryTitle")
    original_title = fields.String(data_key="originalTitle")
    is_adult = fields.Boolean(data_key="isAdult")
    start_year = fields.Number(data_key="startYear", allow_none=True)
    end_year = fields.Number(data_key="endYear", allow_none=True)
    runtime_minutes = fields.Number(data_key="runtimeMinutes", allow_none=True)
    genres = fields.List(fields.String)

    @pre_load
    def clean_values(self, data, **_):
        # remove `\N` for null
        for k, v in data.items():
            if not v or v == r"\N":
                data[k] = None

        # split genre
        try:
            genres = data["genres"].split(",")
        except AttributeError:
            genres = []
        finally:
            data["genres"] = genres if any(genres) else []

        return data
