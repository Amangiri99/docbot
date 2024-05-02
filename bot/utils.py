import openai
import pymongo
from pymongo import ReplaceOne
from django.conf import settings

class OpenAiInteractor:
    def __init__(self) -> None:
        self.model_name = settings.MODEL_NAME
    
    @staticmethod
    def generate_embeddings(instance, text):
        """
        Function to generate embeddings for a text.
        """
        return openai.embeddings.create(
            input=[text], model=instance.model_name
        ).data[0].embedding

class PyMongoDriver:
    def __init__(self) -> None:
        self.client = pymongo.MongoClient(settings.MONGODB_ATLAS_CLUSTER_URI)
        self.db_name = self.client[settings.MONGO_DB_NAME]
        self.collection_name = self.db_name[settings.COLLECTION_NAME]
        self.atlas_vector_search_index_name = settings.ATLAS_VECTOR_SEARCH_INDEX_NAME
        self.embedding_field_name = settings.EMBEDDING_FIELD_NAME
        self.model_name = settings.MODEL_NAME
        self.vector_index_dimension = settings.VECTOR_INDEX_DIMENSION

    def create_vector_embedding(self):
        """
        Function to create vector embedding
        """
        # Update the collection with the embeddings
        requests = []

        for doc in self.collection_name.find({'plot':{"$exists": True}}).limit(500):
            doc[self.EMBEDDING_FIELD_NAME] = OpenAiInteractor.generate_embedding(doc['plot'])
        requests.append(ReplaceOne({'_id': doc['_id']}, doc))

        self.collection_name.bulk_write(requests)
    
    def create_vector_search_index(self):
        """
        Function to create a vector search index in the mongo db. 
        """
        self.collection_name.create_search_index({
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
        return self.collection_name.aggregate([{
            '$vectorSearch': {
                "index": self.atlas_vector_search_index_name,
                "path": self.embedding_field_name,
                "queryVector": OpenAiInteractor.generate_embedding(query),
                "numCandidates": 50,
                "limit": total_response_required,
            }
        }])
