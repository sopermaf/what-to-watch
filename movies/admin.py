from django.contrib import admin

from movies.models import Genre, TitleType, WatchItem

# Register your models here.
admin.site.register(Genre)
admin.site.register(TitleType)


@admin.register(WatchItem)
class WatchItemAdmin(admin.ModelAdmin):
    list_display = (
        "primary_title",
        "average_rating",
        "start_year",
        "num_votes",
        "imdb_id",
    )
