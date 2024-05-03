import datetime

from django.conf import settings

from rest_framework import serializers as rest_serializers
from bot import (
    constants as bot_constants,
    utils as bot_utils,
)


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
    Serializer to parse project name and created.
    """

    project_name = rest_serializers.CharField(max_length=128, required=True)
    created_at = rest_serializers.DateTimeField(default=datetime.datetime.now())

    def save(self, **kwargs):
        query = {"project_name": self.validated_data["project_name"]}
        update_operation = {"$set": self.validated_data}
        return bot_utils.PyMongoDriver().create_update_document(
            query, update_operation, bot_constants.PROJECT_COLLECTION_NAME
        )
