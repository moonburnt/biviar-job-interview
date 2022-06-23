from django.urls import path
from . import views

urlpatterns = (
    # everyone
    path("courses/", views.CoursesView.as_view()),
    # lector and students
    path("courses/<int:course_id>", views.CourseView.as_view()),
    path("courses/<int:course_id>/add_student", views.AddStudentToCourseView.as_view()),
    path(
        "courses/<int:course_id>/remove_student",
        views.RemoveStudentFromCourseView.as_view(),
    ),
    path(
        "courses/<int:course_id>/add_lector",
        views.AddLectorToCourseView.as_view(),
    ),
    path("courses/my", views.MyCoursesView.as_view()),
    path("courses/<int:course_id>/lections", views.CourseLectionsView.as_view()),
    path(
        "courses/<int:course_id>/lections/<int:lection_id>", views.LectionView.as_view()
    ),
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework",
        views.HomeworkView.as_view(),
    ),
    path("courses/<int:course_id>/lectors", views.CourseLectorsView.as_view()),
    # this endpoint should return homework's solution
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework/<int:student_id>",
        views.HomeworkSolutionView.as_view(),
    ),
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework/<int:student_id>/rate",
        views.RateHomeworkSolutionView.as_view(),
    ),
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework/<int:student_id>/comments",
        views.CommentsView.as_view(),
    ),
    # lector-only
    path(
        "courses/<int:course_id>/lections/add_lection",
        views.AddLectionView.as_view(),
    ),
    path("courses/<int:course_id>/students", views.CourseStudentsView.as_view()),
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/add_homework",
        views.AddHomeworkView.as_view(),
    ),
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework/solutions",
        views.HomeworkSolutionsView.as_view(),
    ),
    # student-only
    path(
        "courses/<int:course_id>/lections/<int:lection_id>/homework/add_solution",
        views.AddHomeworkSolutionView.as_view(),
    ),
)
