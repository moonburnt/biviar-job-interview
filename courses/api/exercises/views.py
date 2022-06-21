from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from exercises.models import Course, Lection
from . import serializers

# All courses, does not require auth. May change that later
class CoursesView(generics.ListCreateAPIView):
    serializer_class = serializers.CoursesSerializer
    queryset = Course.objects.all()


# Personal courses, require auth to decide which ones to show
class MyCoursesView(generics.ListAPIView):
    serializer_class = serializers.CoursesSerializer
    permission_classes = (IsAuthenticated,)

    # I think this will do?
    # queryset = User.objects.filter(student_courses)
    def get_queryset(self):
        user = self.request.user

        if user.usertype == User.LECTOR:
            return (
                Course.objects.filter(author=user)
                .all()
                .union(Course.objects.filter(co_authors=user).all())
            )

        elif user.usertype == User.STUDENT:
            return Course.objects.filter(students=user).all()

        elif user.usertype == User.STAFF:
            return Course.objects.all()

        else:
            # This should not happen, doing as a safety measure
            raise ValueError(f"Invalid usertype: {user.usertype}")


# class MyLectionsView(generics.ListAPIView):
#     serializer_class = serializers.LectionsSerializer
#     permission_classes = (IsAuthenticated,)

#     def get_queryset(self):
#         user = self.request.user

#         if user.usertype == User.LECTOR:
#             return User.objects.prefetch_related("lections").all()

#         elif user.usertype == User.STUDENT:
#             return User.objects.prefetch_related("student_lections").all()

#         elif user.usertype == User.STAFF:
#             return Lection.objects.all()

#         else:
#             raise ValueError(f"Invalid usertype: {user.usertype}")


class CourseView(generics.RetrieveAPIView):
    serializer_class = serializers.CoursesSerializer
    queryset = Course.objects.all()

    lookup_url_kwarg = "course_id"


class CourseLectionsView(generics.ListCreateAPIView):
    serializer_class = serializers.LectionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        course_id = self.kwargs["course_id"]

        lections = Lection.objects.filter(course_id=course_id)

        user = self.request.user

        if user.usertype == User.LECTOR:
            return (
                lections.filter(course__author=user)
                .union(lections.filter(course__co_authors=user))
                .union(lections.filter(author=user))
            )

        elif user.usertype == User.STUDENT:
            return lections.filter(course__students=user)

        elif user.usertype == User.STAFF:
            return lections

        else:
            raise ValueError("Invalid user type")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_id"] = self.kwargs["course_id"]
        return context
