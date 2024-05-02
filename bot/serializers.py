# serializers.py
from rest_framework import serializers

class QuestionResponseSerializer(serializers.Serializer):
    "Serializer to validate given input, create/store embeddings & fetch result of question"
    question = serializers.CharField(max_length=1000)
    project_id = serializers.IntegerField()
