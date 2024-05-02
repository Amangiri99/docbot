from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from bot import serializers


class QuestionResponseView(APIView):
    """
    API to convert given question into vector & fetch the corresponding result
    """
    def post(self, request, *args, **kwargs):
        # Deserialize the input data
        serializer = serializers.QuestionResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the utility function to generate embeddings
        response = ''
        # response = generate_embeddings(input_string, input_number)

        # Return the embeddings as response
        return Response(response)
