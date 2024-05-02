import openai
import pymongo
from django.conf import settings

class OpenAiService:

    @staticmethod
    def generate_embeddings(text):
        """
        Function to generate embeddings for a text.
        """
        return openai.embeddings.create(
            input=[text], model=settings.GPT_MODEL_NAME
        ).data[0].embedding


class PyMongoDriver:
    """
    Class with methods to interact with mongodb instance
    """
    _instance = None

    def __new__(cls):
        """Method to create a new instance for the Class"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Creates a singleton class of the pymongo client.
            cls._instance.client = pymongo.MongoClient(settings.MONGODB_ATLAS_CLUSTER_URI)
        return cls._instance

    def __init__(self) -> None:
        """Method to initialize the instance variables."""
        self.db_name = self._instance.client[settings.MONGO_DB_NAME]
        self.collection = self.db_name[settings.COLLECTION_NAME]
        self.atlas_vector_search_index_name = settings.ATLAS_VECTOR_SEARCH_INDEX_NAME
        self.embedding_field_name = settings.EMBEDDING_FIELD_NAME
        self.vector_index_dimension = settings.VECTOR_INDEX_DIMENSION
        self.data_field_name = settings.DATA_FIELD_NAME
        self.number_of_neighbours = settings.NUMBER_OF_NEIGHBOURS

    def create_vector_document(self, data, vector, file_name, project_name):
        """
        Function to create vector embedding
        :param data: The data to be stored in the db.
        :param vector: The vector generated for the data.
        :param file_name: The name of the file.
        :param project_name: The name of the project.
        """
        self.collection.insert_one({
            "data": data,
            "vector": vector,
            "file_name": file_name,
            "project_name": project_name
        })

    def create_vector_search_index(self):
        """
        Function to create a vector search index in the mongo db. 
        """
        self.collection.create_search_index({
            "fields": [{
                "numDimensions": self.vector_index_dimension,
                "path": self.embedding_field_name,
                "similarity": "dotProduct",
                "type": "vector"
            }]
        })

    def get_results(self, query, total_response_required):
        """
        Function to get result from the vector search table
        :param query: The query to be made
        :param total_response_required: total number of response to be sent.
        """
        return self.collection.aggregate([
            {'$match': { 'project': query['project'] }},
            {
                '$vectorSearch': {
                    "index": self.atlas_vector_search_index_name,
                    "path": self.embedding_field_name,
                    "queryVector": OpenAiService.generate_embeddings(query['data']),
                    "numCandidates": self.number_of_neighbours,
                    "limit": total_response_required,
                }
            }
        ])
