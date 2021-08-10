import django_filters
from django_filters import ChoiceFilter, DateRangeFilter
from . models import Note
class NoteFilter(django_filters.FilterSet):
    updated_on = DateRangeFilter(label = "Date")
    class Meta:
        model = Note
        fields = ['title','subject','updated_on']