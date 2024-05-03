import datetime

from django.conf import settings

from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
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
        
        # splitting contents into chunks
        textSplitter = CharacterTextSplitter()
        chunks = textSplitter.split_text(content.decode('utf-8'))
        
        # converting chunks to documents
        docs = [Document(page_content=chunk) for chunk in chunks]

        # load llm model
        llm_model = bot_utils.load_llm()

        # create summary using the model
        chain = load_summarize_chain(llm_model, chain_type='map_reduce')
        response = chain.invoke(docs)
        
        bot_utils.PyMongoDriver().create_vector_document(
            response['output_text'],
            self.validated_data["file_name"],
            self.validated_data["project_name"],
        )
        for chunk in chunks:
            bot_utils.PyMongoDriver().create_vector_document(
                chunk,
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
