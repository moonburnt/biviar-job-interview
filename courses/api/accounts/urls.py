from django.urls import path
from . import views

urlpatterns = (
    path("students/", views.StudentsView.as_view()),
    path("students/register", views.StudentsRegistrationView.as_view()),
    path("lectors/register", views.LectorsRegistrationView.as_view()),
)
