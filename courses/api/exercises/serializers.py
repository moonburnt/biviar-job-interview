from rest_framework import serializers
from exercises.models import Lection, Homework


class LectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lection
        fields = "__all__"


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = "__all__"


class HomeworkCreation(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = "__all__"

    # name = serializers.CharField(max_length=50)
    # description = serializers.CharField(max_length = 1000)
    # # TODO: add pdf payload

    # # Integer coz our id is django.db.models.BigAutoField
    # lection_id = serializers.IntegerField()

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
