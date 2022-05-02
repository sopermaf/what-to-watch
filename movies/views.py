from django.core.exceptions import BadRequest
from django.shortcuts import render

from movies.forms import FilterMovie
from movies.models import WatchItem


def index(request):
    try:
        minimum_rating = request.GET.get("minimum_rating")
        if minimum_rating:
            minimum_rating = float(minimum_rating)
    except ValueError:
        raise BadRequest("minimum_rating must be numeric")

    # TODO: this will be ineffecient
    movie = None
    if minimum_rating:
        movies = WatchItem.objects.order_by("?").filter(
            average_rating__gte=minimum_rating
        )
        if movies:
            movie = movies[0]

    context = {"movie": movie, "form": FilterMovie()}
    return render(request, "movies/index.html", context)
