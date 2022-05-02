from django.contrib import admin

from movies.models import Genre, TitleType, WatchItem

# Register your models here.
admin.site.register(WatchItem)
admin.site.register(Genre)
admin.site.register(TitleType)
