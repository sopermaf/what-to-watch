from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class TitleType(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

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
        return self.imdb_id

    @property
    def imdb_link(self) -> str:
        return f"https://www.imdb.com/title/{self.imdb_id}/"

    @classmethod
    def create_watch_item(cls, watch_item: dict):
        genres = watch_item.pop("genres")
        genres = [Genre.objects.get_or_create(name=genre)[0] for genre in genres]

        title_type, _ = TitleType.objects.get_or_create(name=watch_item["title_type"])
        watch_item["title_type"] = title_type

        watch_item, _ = WatchItem.objects.update_or_create(
            imdb_id=watch_item.pop("imdb_id"), defaults=watch_item
        )

        watch_item.genres.add(*genres)
        watch_item.title_type = title_type
        watch_item.save()
