from django.urls import path
from . import views

urlpatterns = (
    path("courses/", views.CoursesView.as_view()),
    # TODO: maybe move this to personal account
    path("courses/my", views.MyCoursesView.as_view()),
    path("courses/<int:course_id>", views.CourseView.as_view()),
    path("courses/<int:course_id>/lections", views.CourseLectionsView.as_view()),
    # TODO:
    # lector and students
    # - courses/{course_id}/lections/{lection_id}
    # - courses/{course_id}/lections/{lection_id}/homework
    # - courses/{course_id}/lectors/
    #
    # student-only
    # - homeworks/my/
    # - courses/{course_id}/lections/{lection_id}/homework/{student_id}/solution/upload
    #
    # TODO: replace /add with under-the-hood post requests, remove with delete
    # lector-only
    # - courses/{course_id}/lections/add
    # - courses/{course_id}/lections/{lection_id}/homework/add
    # - courses/{course_id}/lections/{lection_id}/homework/stats
    # - courses/{course_id}/lections/{lection_id}/homework/stats/solved
    # - courses/{course_id}/lections/{lection_id}/homework/stats/unsolved
    # - courses/{course_id}/lections/{lection_id}/homework/{student_id}/rating/add
    #
    # TODO: maybe add ability to also remove lectors
    # - courses/{course_id}/lectors/add
    # - courses/{course_id}/students/
    # - courses/{course_id}/students/add
    # - courses/{course_id}/students/remove
    #
    # lector and specific student
    # - courses/{course_id}/lections/{lection_id}/homework/{student_id}/solution/
    # - courses/{course_id}/lections/{lection_id}/homework/{student_id}/rating
    # - courses/{course_id}/lections/{lection_id}/homework/{student_id}/rating/comments
    # - courses/{course_id}/lections/{lection_id}/homework/{student_id}/rating/comments/add
)
