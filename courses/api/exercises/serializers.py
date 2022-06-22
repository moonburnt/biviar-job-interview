from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from exercises.models import (
    Lection,
    Homework,
    Course,
    HomeworkSolution,
    Comment,
)
from accounts.models import User


class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "name", "description", "author")
        read_only_fields = ("author",)

    # TODO: maybe hide completed courses from queue
    def validate(self, attrs):
        user = self.context["request"].user

        if user.is_anonymous:
            raise serializers.ValidationError(
                "Only registered users can create courses"
            )

        if user.usertype != User.LECTOR:
            raise serializers.ValidationError("You must be a lector to create a course")

        attrs["author"] = user
        return attrs


class LectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lection
        fields = "__all__"
        read_only_fields = ("author", "course")

    def validate(self, attrs):
        user = self.context["request"].user

        if user.usertype != User.LECTOR:
            raise serializers.ValidationError(
                "You must be a lector to create a lection"
            )

        attrs["author"] = user
        attrs["course_id"] = self.context["course_id"]
        return attrs


class HomeworksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = "__all__"
        # I think?
        read_only_fields = ("lection",)

    def validate(self, attrs):
        user = self.context["request"].user

        if user.usertype == user.LECTOR:
            if user == homework.objects.lection.get("author"):
                attrs["lection"] = self.context["lection_id"]

                return attrs

        raise serializers.ValidationError(
            "You must be this course's lector to set lection's homework"
        )


class HomeworkSolutionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSolution
        fields = "__all__"
        read_only_fields = ("author", "homework")

    def validate(self, attrs):
        user = self.context["request"].user

        if user.usertype == User.STUDENT and user == self.context["student_id"]:
            homework = Homework.objects.get(lection=self.context["lection_id"])
            if not homework:
                raise serializer.ValidationError(
                    "Lection does not exist or does not have any homework set"
                )

            attrs["homework"] = homework
            attrs["author"] = user
            return attrs

        raise serializers.ValidationError(
            "You must be a student with access to this lection to upload homework"
        )


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("author", "homework")

    def validate(self, attrs):
        user = self.context["request"].user

        homework = Homework.objects.get(lection=self.context["lection_id"])
        if not homework:
            raise serializer.ValidationError(
                "Lection does not exist or does not have any homework set"
            )

        if (user.usertype == User.STUDENT and user == self.context["student_id"]) or (
            user.usertype == User.LECTOR and user == homework.lection.author
        ):
            attrs["author"] = user
            attrs["homework"] = homework

            return attrs

        raise serializers.ValidationError(
            "You must be the author of this homework or lector to add comments"
        )


class BaseCourseUserOperationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    course_id = serializers.IntegerField(read_only=True)

    def validate_user_id(self, value):
        user = User.objects.filter(id=value).first()
        if not user:
            raise serializers.ValidationError("User not found")

        return user

    def validate(self, attrs):
        course_id = self.context["course_id"]
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise serializers.ValidationError("Course not found")

        author = self.context["request"].user
        if (
            not course.co_authors.filter(id=author.id).first()
            and course.author != author
        ):
            raise serializers.ValidationError(
                "You must be course's author or lector to do that"
            )

        self._check(course, attrs["user_id"])

        attrs["course"] = course

        return attrs

    # We need create coz its not a model serializer
    def create(self, validated_data):
        user = validated_data["user_id"]
        course = validated_data["course"]

        # course.students.add(user)
        self._action(course, user)
        return {
            "user_id": user.id,
            "course_id": course.id,
        }

    def _action(self, course, user):
        pass

    def _check(self, course, user):
        pass

    def _check_permissions(self, author, course):
        pass


class AddStudentToCourseSerializer(BaseCourseUserOperationSerializer):
    def _action(self, course, user):
        course.students.add(user)

    def _check(self, course, user):
        if user.usertype != User.STUDENT:
            raise serializers.ValidationError("User is not a student")

        if course.students.filter(id=user.id).first():
            raise serializers.ValidationError(
                "Student is already participating in this course"
            )


# Post request
class RemoveStudentFromCourseSerializer(BaseCourseUserOperationSerializer):
    def _action(self, course, user):
        course.students.remove(user)

    def _check(self, course, user):
        if user.usertype != User.STUDENT:
            raise serializers.ValidationError("User is not a student")

        if not course.students.filter(id=user.id).first():
            raise serializers.ValidationError("Student does not belong to this course")


class AddLectorToCourseSerializer(BaseCourseUserOperationSerializer):
    def _action(self, course, user):
        course.co_authors.add(user)

    def _check(self, course, user):
        if user.usertype != User.LECTOR:
            raise serializers.ValidationError("User is not a lector")

        if course.co_authors.filter(id=user.id).first() or course.author == user:
            raise serializers.ValidationError("Lector already belongs to this course")


class RateHomeworkSolutionSerializer(serializers.Serializer):
    student_id = serializers.IntegerField(read_only=True)
    lection_id = serializers.IntegerField(read_only=True)
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    def validate_student(self, value):
        user = User.objects.filter(id=value).first()
        if not user:
            raise serializers.ValidationError("Student not found")

        return user

    def validate(self, attrs):
        lection_id = attrs["lection_id"]
        student = attrs["student_id"]

        author = self.context["request"].user

        lection = Lection.objects.filter(
            id=lection_id,
            author=author,
        ).first()

        if not lection:
            raise serializers.ValidationError("You must be lector to do that")

        homework = HomeworkSolution.objects.filter(
            author__id=student,
            homework__lection__id=lection_id,
        ).first()

        if not homework:
            raise serializers.ValidationError("Homework not found")

        attrs["solution"] = homework
        return attrs

    def create(self, validated_data):
        solution = validated_data["solution"]
        rating = validated_data["rating"]

        solution.rating = rating
        solution.save()

        return {
            "lection_id": validated_data["lection_id"],
            "student_id": validated_data["student_id"],
            "rating": validated_data["rating"],
        }
