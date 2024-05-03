import json
import pymongo
from openai import embeddings, OpenAI

from django.conf import settings


class OpenAIService:
    def search_message_in_docs(self, query, documents):
        """
        Function to create a message using user query & relevant documents
        """

        # Prepare the message with the message and documents
        message = f"My question: {query}\nAnswer using:\n"
        for doc in documents:
            message += f"- {doc}\n"

        try:
            # Call the OpenAI GPT model to generate a response
            response = OpenAI().chat.completions.create(
                model=settings.GPT_MODEL_NAME,
                messages=[{"role": "user", "content": message}],
            )
            # Extract the response text
            return json.loads(response.model_dump_json())["choices"][0]["message"][
                "content"
            ]
        except:
            return "Unable to process your query, please try again"

    @staticmethod
    def generate_embeddings(text):
        """
        Function to generate embeddings for a text.
        """
        return (
            embeddings.create(input=[text], model=settings.EMBEDDINGS_MODEL_NAME)
            .data[0]
            .embedding
        )


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
            cls._instance.client = pymongo.MongoClient(
                settings.MONGODB_ATLAS_CLUSTER_URI
            )
        return cls._instance

    def __init__(self) -> None:
        """Method to initialize the instance variables."""
        self.db_name = self._instance.client[settings.MONGO_DB_NAME]
        self.collection = self.db_name[settings.COLLECTION_NAME]
        self.project_collection = self.db_name[settings.PROJECT_COLLECTION_NAME]
        self.atlas_vector_search_index_name = settings.ATLAS_VECTOR_SEARCH_INDEX_NAME
        self.embedding_field_name = settings.EMBEDDING_FIELD_NAME
        self.vector_index_dimension = settings.VECTOR_INDEX_DIMENSION
        self.data_field_name = settings.DATA_FIELD_NAME
        self.number_of_candidates = settings.NUMBER_OF_CANDIDATES
        self.nearest_doc_count = settings.NEAREST_DOC_COUNT

    def create_vector_document(self, data, vector, file_name, project_name):
        """
        Function to create vector embedding
        :param data: The data to be stored in the db.
        :param vector: The vector generated for the data.
        :param file_name: The name of the file.
        :param project_name: The name of the project.
        """
        self.collection.insert_one(
            {
                "data": data,
                "vector": vector,
                "file_name": file_name,
                "project_name": project_name,
            }
        )

    def get_related_collections(self, question, project_name):
        """
        Function to get k related collections from db
        :param query: The query to be made
        """
        cursor = self.collection.aggregate(
            [
                {
                    "$vectorSearch": {
                        "index": self.atlas_vector_search_index_name,
                        "path": self.embedding_field_name,
                        "queryVector": OpenAIService.generate_embeddings(question),
                        "numCandidates": self.number_of_candidates,
                        "limit": self.nearest_doc_count,
                    }
                },
                {"$match": {"project_name": project_name}},
            ]
        )
        collections = []
        for itr in cursor:
            collections.append(itr["data"])
        return collections

    def create_project(self, data):
        """
        Function to create a project
        """
        query = {"project_name": data["project_name"]}
        update_operation = {"$set": data}
        return self.project_collection.update_one(query, update_operation, upsert=True)

    def get_project_names(self, query):
        """
        Function to return all the collections that matches a query.
        """
        cursor = self.project_collection.find(query)
        documents = []
        for document in cursor:
            documents.append(document)
        return documents
