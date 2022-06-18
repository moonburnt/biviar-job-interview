from rest_framework import generics
from accounts.models import User
from . import serializers


class StudentsView(generics.ListAPIView):
    queryset = User.objects.filter(usertype=User.STUDENT)
    serializer_class = serializers.UserSerializer
