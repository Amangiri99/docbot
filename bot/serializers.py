# serializers.py
from rest_framework import serializers as rest_serializers
from bot import utils as bot_utils


class QuestionResponseSerializer(rest_serializers.Serializer):
    "Serializer to validate given input, create/store embeddings & fetch result of question"
    question = rest_serializers.CharField(max_length=1000)
    project_id = rest_serializers.IntegerField()


class UploadDocSerializer(rest_serializers.Serializer):
    data = rest_serializers.FileField(write_only=True)
    file_name = rest_serializers.CharField()
    project = rest_serializers.CharField()

    def save(self):
        content = self.validated_data['data'].open('r').read()
        bot_utils.PyMongoDriver().create_vector_document(
            content,
            bot_utils.OpenAiService.generate_embeddings(content),
            self.validated_data['file_name'],
            self.validated_data['project']
        )
