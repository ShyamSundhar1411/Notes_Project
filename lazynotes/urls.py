from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('create/',views.create_note,name = "note_create"),
    path('update/<int:pk>/<slug:slug>/',views.NoteUpdateView.as_view(),name = "note_update"),
    path('view/<int:pk>/<slug:slug>/',views.NoteDetailView.as_view(),name = "note_detail"),
    path('delete/<int:pk>/<slug:slug>/',views.NoteDeleteView.as_view(),name = "note_delete")
]
