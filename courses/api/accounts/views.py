from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from . import serializers


class StudentsView(generics.ListAPIView):
    serializer_class = serializers.UserSerializer
    # hide students list from being visible to anon
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # TODO: filter against lector
        lector = self.request.user
        # return User.objects.filter(usertype=User.STUDENT)
        return User.objects.for_lector(lector)


class StudentsRegistrationView(generics.CreateAPIView):
    serializer_class = serializers.StudentRegistration


class LectorsRegistrationView(generics.CreateAPIView):
    serializer_class = serializers.LectorRegistration
