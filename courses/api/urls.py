from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Courses API",
        default_version="v1",
    ),
    # There was no info about allowing/disallowing access to api, so right now
    # its available to everyone
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = (
    path("auth/", include("rest_framework.urls")),
    path("accounts/", include("api.accounts.urls")),
    path("exercises/", include("api.exercises.urls")),
    # swagger
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
)
