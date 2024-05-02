from django.conf import settings

from rest_framework import(
    response as rest_response,
    generics as rest_generics,
    views as rest_views
)

from bot import serializers as bot_serializers


class QuestionResponseView(rest_views.APIView):
    """
    API to convert given question into vector & fetch the corresponding result
    """
    def post(self, request, *args, **kwargs):
        # Deserialize the input data
        serializer = bot_serializers.QuestionResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the utility function to generate embeddings
        response = ''
        # response = generate_embeddings(input_string, input_number)

        # Return the embeddings as response
        return rest_response.Response(response)


# Create your views here.
class UploadDocView(rest_generics.CreateAPIView):
    """
    API to upload document
    """
    serializer_class = bot_serializers.UploadDocSerializer
