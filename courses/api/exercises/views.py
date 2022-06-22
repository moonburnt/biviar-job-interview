from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from exercises.models import Course, Lection, Homework
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
            raise ValueError(f"Invalid usertype: {user.usertype}")


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

    # Injecting serializer with data obtained from url
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_id"] = self.kwargs["course_id"]
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
                raise ValueError("Lector not from this course")

        elif user.usertype == User.STAFF:
            return students

        raise ValueError("Only lectors from this course can access students list")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_id"] = self.kwargs["course_id"]
        return context


class BaseCourseUserOperationView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_id"] = self.kwargs["course_id"]
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

        raise ValueError("Only people who belong to this course can access its lectors")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_id"] = self.kwargs["course_id"]
        return context


class AddLectorToCourseView(BaseCourseUserOperationView):
    serializer_class = serializers.AddLectorToCourseSerializer


class LectionView(generics.RetrieveAPIView):
    serializer_class = serializers.LectionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        lection_id = self.kwargs["lection_id"]

        lection = Lection.objects.get(id=lection_id, course=course_id)

        user = self.request.user

        if user.usertype == User.LECTOR:
            if lection.author == user:
                return lection
            else:
                raise ValueError("Lector isn't the author of this course")

        elif user.usertype == User.STUDENT:
            if Course.objects.filter(id=course_id).get(students=user):
                return lection
            else:
                raise ValueError("Student is not from this course")

        elif user.usertype == User.STAFF:
            return lection

        raise ValueError("Only people from this course can access lection info")


class HomeworkView(generics.CreateAPIView):
    serializer_class = serializers.HomeworksSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # course_id = self.kwargs["course_id"]
        lection_id = self.kwargs["lection_id"]
        user = self.request.user

        homework = Homework.objects.get(lection=lection_id)

        if user.usertype == User.LECTOR:
            if user == homework.objects.lection.get("author"):
                return homework
        elif user.usertype == User.STUDENT:
            # This probably has incorrect format
            if homework.objects.lection.course.filter(students=user):
                return homework
        elif user.usertype == User.STAFF:
            return homework

        raise ValueError("Access Denied")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_id"] = self.kwargs["course_id"]
        context["lection_id"] = self.kwargs["lection_id"]
        return context


class HomeworkSolutionView(generics.CreateAPIView):
    serializer_class = serializers.HomeworkSolutionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        lection_id = self.kwargs["lection_id"]
        student_id = self.kwargs["student_id"]
        user = self.request.user

        homework = Homework.objects.get(lection=lection_id)

        solution = homework.homework_solutions.get(author=student_id)

        # idk if this is corrent format
        if user.usertype == User.STUDENT:
            if student_id == user.id:
                return solution

        elif user.usertype == User.LECTOR:
            if user == homework.lection.get("author"):
                return solution

        elif user.usertype == User.STAFF:
            return solution

        raise ValueError("Access Denied")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # context["course_id"] = self.kwargs["course_id"]
        context["lection_id"] = self.kwargs["lection_id"]
        context["student_id"] = self.kwargs["student_id"]
        return context


class HomeworkSolutionsView(generics.ListAPIView):
    serializer_class = serializers.HomeworkSolutionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        lection_id = self.kwargs["lection_id"]
        user = self.request.user

        homework = Homework.objects.get(lection=lection_id)

        solutions = HomeworkSolution.objects.filter(homework=homework)

        if user.usertype == User.LECTOR:
            if user == homework.objects.lection.get("author"):
                return solutions
        elif user.usertype == User.STAFF:
            return solutions

        raise ValueError("Access Denied")


class RateHomeworkSolutionView(generics.CreateAPIView):
    serializer_class = serializers.RateHomeworkSolutionSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["lection_id"] = self.kwargs["lection_id"]
        context["student_id"] = self.kwargs["student_id"]
        return context


class CommentsView(generics.ListAPIView):
    serializer_class = serializers.CommentsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        lection_id = self.kwargs["lection_id"]
        student_id = self.kwargs["student_id"]
        user = self.request.user

        homework = Homework.objects.get(lection=lection_id)
        solution = homework.homework_solutions.get(author=student_id)

        comments = solution.comments

        # idk if this is correct format
        if user.usertype == User.STUDENT:
            if student_id == user.id:
                return comments

        elif user.usertype == User.LECTOR:
            if user == homework.lection.get("author"):
                return comments

        elif user.usertype == User.STAFF:
            return comments

        raise ValueError("Access Denied")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["lection_id"] = self.kwargs["lection_id"]
        context["student_id"] = self.kwargs["student_id"]
        return context
