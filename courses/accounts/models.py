from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    STAFF = 1
    STUDENT = 2
    LECTOR = 3

    USERTYPE_CHOICES = (
        (STAFF, "Staff"),
        (STUDENT, "Student"),
        (LECTOR, "Lector"),
    )

    usertype = models.PositiveSmallIntegerField(
        choices = USERTYPE_CHOICES,
        default = STUDENT,
    )
