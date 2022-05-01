from django.core.exceptions import BadRequest
from django.shortcuts import render

from movies.models import WatchItem


def index(request):
    try:
        minimum_rating = request.GET.get("minimum_rating")
        if minimum_rating:
            minimum_rating = float(minimum_rating)
    except ValueError:
        raise BadRequest("minimum_rating must be numeric")

    # TODO: this will be ineffecient
    # filter by rating if applicable
    movies = WatchItem.objects.order_by("?")
    if minimum_rating:
        movies = movies.filter(average_rating__gte=minimum_rating)

    context = {"movie": movies[0]}
    return render(request, "movies/index.html", context)
