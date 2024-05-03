import datetime

from rest_framework import serializers as rest_serializers
from bot import utils as bot_utils


class QuestionResponseSerializer(rest_serializers.Serializer):
    """
    Serializer to validate given input, create/store embeddings & fetch result of question
    """

    question = rest_serializers.CharField(max_length=1024)
    project_name = rest_serializers.CharField(max_length=128)


class UploadDocSerializer(rest_serializers.Serializer):
    """
    Serializer to validate incoming data and store file as vector document
    """

    file = rest_serializers.FileField(write_only=True)
    file_name = rest_serializers.CharField()
    project_name = rest_serializers.CharField()

    def save(self):
        content = self.validated_data["file"].open("r").read()
        bot_utils.PyMongoDriver().create_vector_document(
            content,
            bot_utils.OpenAIService.generate_embeddings(content),
            self.validated_data["file_name"],
            self.validated_data["project_name"],
        )


class ProjectNameSerializer(rest_serializers.Serializer):
    """
    Serializer to return a list of all projects
    """

    project_name = rest_serializers.CharField(max_length=128, required=True)
    created_at = rest_serializers.DateTimeField(default=datetime.datetime.now())

    def save(self, **kwargs):
        return bot_utils.PyMongoDriver().create_project(self.validated_data)
