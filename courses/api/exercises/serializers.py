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


class HomeworkSolutionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSolution
        fields = "__all__"


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class HomeworkCreation(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = "__all__"

    # We can validate specific fields, naming for that is validate_{fieldname}
    def validate_lection(self, value):
        lection = Lection.objects.get(id=value)
        if not lection.exists():
            raise serializers.ValidationError("Lection with this id does not exist")

        request = self.context["request"]
        if lection.author != request.user:
            raise serializers.ValidationError(
                "User must be set to lection's lector, to change lection's homework"
            )

        # I think thats about it?
        return value
