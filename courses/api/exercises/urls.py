from django.urls import path
from . import views

urlpatterns = (
    # everyone
    path("courses/", views.CoursesView.as_view()),
    # lector and students
    path("courses/<int:course_id>", views.CourseView.as_view()),
    path("courses/my", views.MyCoursesView.as_view()),
    path("courses/<int:course_id>/lections", views.CourseLectionsView.as_view()),
    path(
        "courses/<int:course_id>/lections/<int:lection_id>", views.LectionView.as_view()
    ),
    # TODO: add ability to set homework by lector
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework",
        views.HomeworkView.as_view(),
    ),
    # TODO: ability to add lectors by other lectors or author
    path("courses/<int:course_id>/lectors", views.CourseLectorsView.as_view()),
    # this endpoint should return homework's solution
    # TODO: ability to upload solution by student
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework/<int:student_id>",
        views.HomeworkSolutionView.as_view(),
    ),
    # TODO: ability to set/update rating by lector
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework/<int:student_id>/rating",
        views.SolutionRatingView.as_view(),
    ),
    # TODO: ability for lector and student to write comments
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework/<intstudent_id>/comments",
        views.CommentsView.as_view(),
    ),
    # lector-only
    # TODO: ability to add and remove students by lectors or author
    path("courses/<int:course_id>/students", views.CourseStudentsView.as_view()),
    path(
        "courses/<int:course_id>/<int:lection_id>/homework/solutions",
        views.HomeworkSolutionsView.as_view(),
    ),
)
