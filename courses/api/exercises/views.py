from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from exercises.models import Course, Lection, Homework, HomeworkSolution, Comment
from django.http import Http404, HttpResponseBadRequest
from . import serializers

from api.accounts.serializers import UserSerializer

# All courses, does not require auth. May change that later
class CoursesView(generics.ListCreateAPIView):
    serializer_class = serializers.CoursesSerializer
    queryset = Course.objects.all()


# Personal courses, require auth to decide which ones to show
class MyCoursesView(generics.ListAPIView):
    serializer_class = serializers.CoursesSerializer
    permission_classes = (IsAuthenticated,)

    # I think this will do?
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
            raise HttpResponseBadRequest(f"Invalid usertype: {user.usertype}")


class CourseView(generics.RetrieveAPIView):
    serializer_class = serializers.CoursesSerializer
    queryset = Course.objects.all()

    lookup_url_kwarg = "course_id"


class CourseLectionsView(generics.ListAPIView):
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
            raise HttpResponseBadRequest("Invalid user type")

    # Injecting serializer with data obtained from url
    def get_serializer_context(self):
        context = super().get_serializer_context()

        course_id = self.kwargs.get("course_id")
        if not course_id:
            raise Http404

        context["course_id"] = course_id
        return context


class CourseStudentsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        user = self.request.user

        course = Course.objects.get(id=course_id)

        students = course.students.all()

        if user.usertype == User.LECTOR:
            # Ensure this lector is from this course
            if user == course.author or course.co_authors.filter(id=user.id):
                return students
            else:
                raise HttpResponseBadRequest("Lector not from this course")

        elif user.usertype == User.STAFF:
            return students

        raise HttpResponseBadRequest(
            "Only lectors from this course can access students list"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        course_id = self.kwargs.get("course_id")
        if not course_id:
            raise Http404

        context["course_id"] = course_id
        return context


class BaseCourseUserOperationView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()

        course_id = self.kwargs.get("course_id")
        if not course_id:
            raise Http404

        context["course_id"] = course_id
        return context


class AddStudentToCourseView(BaseCourseUserOperationView):
    serializer_class = serializers.AddStudentToCourseSerializer


class RemoveStudentFromCourseView(BaseCourseUserOperationView):
    serializer_class = serializers.RemoveStudentFromCourseSerializer


class CourseLectorsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        user = self.request.user

        # This will raise exception if no user has been found, no checks needed
        course = Course.objects.get(id=course_id)

        lectors = course.co_authors.all().union(
            User.objects.filter(id=course.author.id)
        )

        if user.usertype == User.LECTOR:
            # Ensure this lector is from this course
            if user in lectors:
                return lectors

        elif user.usertype == User.STUDENT:
            if course.students.filter(id=user.id):
                return lectors

        elif user.usertype == User.STAFF:
            return lectors

        raise HttpResponseBadRequest(
            "Only people who belong to this course can access its lectors"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        course_id = self.kwargs.get("course_id")
        if not course_id:
            raise Http404

        context["course_id"] = course_id
        return context


class AddLectorToCourseView(BaseCourseUserOperationView):
    serializer_class = serializers.AddLectorToCourseSerializer


class AddLectionView(generics.CreateAPIView):
    serializer_class = serializers.AddLectionSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        course_id = self.kwargs.get("course_id")
        if not course_id:
            raise Http404

        context["course_id"] = course_id
        return context


class LectionView(generics.RetrieveAPIView):
    serializer_class = serializers.LectionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        course_id = self.kwargs["course_id"]
        lection_id = self.kwargs["lection_id"]

        lection = Lection.objects.get(id=lection_id, course__id=course_id)

        user = self.request.user

        if user.usertype == User.LECTOR:
            if lection.author == user:
                return lection
            else:
                raise HttpResponseBadRequest("Lector isn't the author of this course")

        elif user.usertype == User.STUDENT:
            if Course.objects.filter(id=course_id).get(students=user):
                return lection
            else:
                raise HttpResponseBadRequest("Student is not from this course")

        elif user.usertype == User.STAFF:
            return lection

        raise HttpResponseBadRequest(
            "Only people from this course can access lection info"
        )


class HomeworkView(generics.RetrieveAPIView):
    serializer_class = serializers.HomeworksSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        course_id = self.kwargs["course_id"]
        lection_id = self.kwargs["lection_id"]
        user = self.request.user

        homework = Homework.objects.filter(lection=lection_id).first()
        if not homework:
            raise HttpResponseBadRequest("Homework has not been set")

        if homework.lection.course.id != course_id:
            raise HttpResponseBadRequest("Course does not have such lection")

        if user.usertype == User.LECTOR:
            if user == homework.lection.author:
                return homework
        elif user.usertype == User.STUDENT:
            if Course.objects.filter(id=course_id, students=user).first():
                return homework
        elif user.usertype == User.STAFF:
            return homework

        raise HttpResponseBadRequest("Access Denied")

    def get_serializer_context(self):
        context = super().get_serializer_context()

        course_id = self.kwargs.get("course_id")
        if not course_id:
            raise Http404

        context["course_id"] = course_id

        lection_id = self.kwargs.get("lection_id")
        if not lection_id:
            raise Http404
        context["lection_id"] = lection_id

        return context


class AddHomeworkView(generics.CreateAPIView):
    serializer_class = serializers.AddHomeworkSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lection_id = self.kwargs.get("lection_id")
        if not lection_id:
            raise Http404
        context["lection_id"] = lection_id
        return context


class HomeworkSolutionView(generics.RetrieveAPIView):
    serializer_class = serializers.HomeworkSolutionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        lection_id = self.kwargs["lection_id"]
        student_id = self.kwargs["student_id"]
        user = self.request.user

        homework = Homework.objects.filter(lection=lection_id).first()
        if not homework:
            raise HttpResponseBadRequest("Lection does not have a homework")

        solution = HomeworkSolution.objects.filter(
            author=student_id,
            homework=homework,
        ).first()
        if not solution:
            raise HttpResponseBadRequest("Solution not found")

        if user.usertype == User.STUDENT:
            if student_id == user.id:
                return solution

        elif user.usertype == User.LECTOR:
            if user == homework.lection.author:
                return solution

        elif user.usertype == User.STAFF:
            return solution

        raise HttpResponseBadRequest("Access Denied")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lection_id = self.kwargs.get("lection_id")
        if not lection_id:
            raise Http404
        context["lection_id"] = lection_id

        student_id = self.kwargs.get("student_id")
        if not student_id:
            raise Http404
        context["student_id"] = student_id
        return context


class AddHomeworkSolutionView(generics.CreateAPIView):
    serializer_class = serializers.AddHomeworkSolutionSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lection_id = self.kwargs.get("lection_id")
        if not lection_id:
            raise Http404
        context["lection_id"] = lection_id
        return context


class HomeworkSolutionsView(generics.ListAPIView):
    serializer_class = serializers.HomeworkSolutionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        lection_id = self.kwargs["lection_id"]
        user = self.request.user

        homework = Homework.objects.filter(lection=lection_id).first()
        if not homework:
            raise HttpResponseBadRequest("Homework not found")

        solutions = HomeworkSolution.objects.filter(homework=homework).all()

        if user.usertype == User.LECTOR:
            if user == homework.lection.author:
                return solutions
        elif user.usertype == User.STAFF:
            return solutions

        raise HttpResponseBadRequest("Access Denied")


class RateHomeworkSolutionView(generics.CreateAPIView):
    serializer_class = serializers.RateHomeworkSolutionSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lection_id = self.kwargs.get("lection_id")
        if not lection_id:
            raise Http404
        context["lection_id"] = lection_id

        student_id = self.kwargs.get("student_id")
        if not student_id:
            raise Http404
        context["student_id"] = student_id
        return context


class CommentsView(generics.ListCreateAPIView):
    serializer_class = serializers.CommentsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        lection_id = self.kwargs["lection_id"]
        student_id = self.kwargs["student_id"]
        user = self.request.user

        homework = Homework.objects.filter(lection=lection_id).first()
        if not homework:
            raise HttpResponseBadRequest("Homework not found")

        solution = HomeworkSolution.objects.filter(
            author__id=student_id,
            homework=homework,
        ).first()

        if not solution:
            raise HttpResponseBadRequest("Homework solution not found")

        comments = Comment.objects.filter(
            homework=homework,
        ).all()

        # idk if this is correct format
        if user.usertype == User.STUDENT:
            if user.id == student_id:
                return comments

        elif user.usertype == User.LECTOR:
            if user == homework.lection.author:
                return comments

        elif user.usertype == User.STAFF:
            return comments

        raise HttpResponseBadRequest("Access Denied")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lection_id = self.kwargs.get("lection_id")
        if not lection_id:
            raise Http404
        context["lection_id"] = lection_id

        student_id = self.kwargs.get("student_id")
        if not student_id:
            raise Http404
        context["student_id"] = student_id
        return context
