from django.urls import path

from . import views

app_name = "scores"

urlpatterns = [
    path("create/", views.create_score, name="create_score"),
    path("read/<slug:slug>/", views.read_score, name="read_score"),
    path("update/<slug:slug>/", views.update_score, name="update_score"),
    path("delete/<slug:slug>/", views.delete_score, name="delete_score"),
]
