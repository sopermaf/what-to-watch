from django.urls import path
from django.views.generic import TemplateView

app_name = "movies"

urlpatterns = [
    path("", TemplateView.as_view(template_name="movies/home.html")),
]
