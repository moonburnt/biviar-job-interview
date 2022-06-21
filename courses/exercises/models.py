from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class HomeworkSolution(models.Model):
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.RESTRICT,
        related_name="homework_solutions",
    )

    homework = models.ForeignKey(
        "exercises.Homework",
        on_delete=models.CASCADE,
        related_name="homework_solutions",
    )

    # For now, solution can only be text
    solution = models.TextField(
        max_length=1000,
    )

    rating = models.IntegerField(
        # This is hardcoded to work with 5-tier rating systems.
        # Will need adjustments if this is planned to be used in location with
        # rating systems other than 1-5
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )


class Comment(models.Model):
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    # homework, this comment is attached to
    homework = models.ForeignKey(
        "exercises.Homework",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    text = models.TextField(
        max_length=1000,
    )


class Lection(models.Model):
    name = models.TextField(max_length=50)
    description = models.TextField(max_length=1000)

    # Check for usertype should happen on request, before lection's creation
    author = models.ForeignKey(
        # Using string names instead of model's class coz one app may reference
        # to models from other app and this would be better for that
        "accounts.User",
        on_delete=models.CASCADE,
        # I think this will do?
        related_name="lections",
    )

    # TODO:
    # - store presentation's pdfs somewhere
    # - add field with path to attached pdf

    # one lection may only have one course, for now
    course = models.ForeignKey(
        "exercises.Course",
        on_delete=models.CASCADE,
        related_name="lections",
    )


class Homework(models.Model):
    name = models.TextField(max_length=50)
    description = models.TextField(max_length=1000)

    # The lection, this homework is attached to. Some lections may have none.
    # One lection can only have one homework at a time and one homework can only
    # be attached to one lection.
    lection = models.OneToOneField(
        "exercises.Lection",
        on_delete=models.CASCADE,
        # This will create backwards reference to homework from Lection
        related_name="homework",
    )


class Course(models.Model):
    name = models.TextField(max_length=50)
    description = models.TextField(max_length=1000)

    # Master of course, can't be removed by other lectors
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="author_courses",
    )

    # other teachers. many-to-many, coz:
    # - lectors may have multiple courses
    # - course may have multiple lections
    co_authors = models.ManyToManyField(
        "accounts.User",
        related_name="co_author_courses",
    )

    students = models.ManyToManyField(
        "accounts.User",
        related_name="student_courses",
    )
