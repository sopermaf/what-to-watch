from django import forms


class FilterMovie(forms.Form):
    minimum_rating = forms.fields.FloatField(min_value=0.1, max_value=10, required=True)
