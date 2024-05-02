from django.urls import path
from bot import views as bot_views

urlpatterns = [
    path('question-response', bot_views.QuestionResponseView.as_view(), name='get_question_response'),
]
