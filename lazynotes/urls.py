from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('create/',views.create_note,name = "note_create"),
    path('update/<int:pk>/<slug:slug>/',views.NoteUpdateView.as_view(),name = "note_update"),
    path('view/<int:pk>/<slug:slug>/',views.NoteDetailView.as_view(),name = "note_detail"),
    path('delete/<int:pk>/<slug:slug>/',views.NoteDeleteView.as_view(),name = "note_delete"),
    path('render/pdf/<int:pk>/download/',views.render_to_pdf_download_view,name = "render_to_pdf_download"),
    path('render/pdf/<int:pk>/send/email/',views.render_to_pdf_mail_view,name = "render_to_pdf_mail"),
    path('view/all/',views.viewallnotes,name = "view_all_notes"),
]
