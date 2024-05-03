from rest_framework import(
    response as rest_response,
    generics as rest_generics,
    views as rest_views
)

from bot import serializers as bot_serializers, utils as bot_utils


class QuestionResponseView(rest_views.APIView):
    """
    API to convert given question into vector & fetch the corresponding result
    """
    def post(self, request):
        serializer = bot_serializers.QuestionResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Get related collections
        related_collections = bot_utils.PyMongoDriver().get_related_collections(
            validated_data['question'], validated_data['project_name']
        )
        # Pass related documents to GPT for response
        response = bot_utils.OpenAIService().search_message_in_docs(
            validated_data['question'], related_collections
        )

        return rest_response.Response({ response })


# Create your views here.
class UploadDocView(rest_generics.CreateAPIView):
    """
    API to upload document to a specific project
    """
    serializer_class = bot_serializers.UploadDocSerializer
