from django.urls import path
from bot import views as bot_views

urlpatterns = [
    path(
        "question-response",
        bot_views.QuestionResponseView.as_view(),
        name="get_question_response",
    ),
    path("upload/doc", bot_views.UploadDocView.as_view(), name="upload_doc"),
    path("projects/", bot_views.GetProjectName.as_view(), name="get_projects_name"),
]
