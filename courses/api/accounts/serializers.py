from rest_framework import serializers
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = "__all__"
        # Exclude passwords from users view output
        exclude = ("password",)


class BaseRegistration(serializers.Serializer):
    usertype = None

    username = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    # write only means it wont be returned
    password = serializers.CharField(max_length=30, write_only=True)

    def validate(self, attrs):
        username = attrs["username"]
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("User with this username already exists")

        email = attrs["email"]
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")

        return attrs

    def create(self, attrs):
        username = attrs["username"]
        email = attrs["email"]
        password = attrs["password"]

        user = User(
            username=username,
            email=email,
            usertype=self.usertype,
        )

        user.set_password(password)
        user.save()

        return user


class StudentRegistration(BaseRegistration):
    usertype = User.STUDENT


class LectorRegistration(BaseRegistration):
    usertype = User.LECTOR


# staff will be registered only via admin menu
