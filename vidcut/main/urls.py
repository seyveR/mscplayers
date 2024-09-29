from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("forgot", views.forgot, name="forgot"),
    path(" /upload_video/", views.upload_file, name="upload_video"),
    path(" /upload_link_rube/", views.upload_link_rube, name="upload_link_rube"),
    path(" /models_start_cutting/", views.models_start_cutting, name="models_start_cutting"),
    path(" /answer_vids/", views.answer_vids, name="answer_vids"),
]
