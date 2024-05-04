from django.conf import settings

from rest_framework import (
    response as rest_response,
    generics as rest_generics,
    views as rest_views,
)

from bot import (
    constants as bot_constants,
    serializers as bot_serializers,
    utils as bot_utils,
)


class QuestionResponseView(rest_views.APIView):
    """
    API to convert given question into vector & fetch the corresponding result
    """

    def post(self, request):
        serializer = bot_serializers.QuestionResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        mongo_driver = bot_utils.PyMongoDriver()
        last_chat_records = mongo_driver.get_documents(
            collection=settings.COLLECTION_NAME,
            query={"project_name": {"$eq": validated_data["project_name"]}},
            projection={"vector": 0},
            options={
                "limit": settings.TOTAL_PAST_CHAT_TO_INCLUDE,
                "sort": {"created_at": -1},
            },
        )
        if last_chat_records:
            prompt_message = "\n".join(
                chat_record["data"] for chat_record in last_chat_records
            )
            prompt_message += "\nHere is a list of answers that might be similar to this topic, use them if they are somewhow related to the question or generate your own."

        # Get related collections
        related_collections = mongo_driver.get_related_collections(
            validated_data["question"], validated_data["project_name"]
        )
        # Pass related documents to GPT for response
        response = bot_utils.OpenAIService().search_message_in_docs(
            validated_data["question"],
            related_collections,
            additional_prompt_message=prompt_message,
        )
        data = f"Previously asked Question:{validated_data['question']}\nAnswer for the previously asked question:{response}"
        mongo_driver.create_vector_document(
            data=data,
            file_name=last_chat_records[0]["file_name"],
            project_name=validated_data["project_name"],
        )

        return rest_response.Response({"response": response})


# Create your views here.
class UploadDocView(rest_generics.CreateAPIView):
    """
    API to upload document to a specific project
    """

    serializer_class = bot_serializers.UploadDocSerializer


class GetProjectName(rest_generics.ListCreateAPIView):
    """
    API to get or create projects
    """

    serializer_class = bot_serializers.ProjectNameSerializer

    def get_queryset(self):
        return bot_utils.PyMongoDriver().get_documents(
            collection=bot_constants.PROJECT_COLLECTION_NAME,
            query={},
        )
