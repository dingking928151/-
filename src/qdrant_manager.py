import logging
from qdrant_client import QdrantClient, models

class QdrantManager:
    def __init__(self, host: str, port: int)
        self.client = QdrantClient(host=host, port=port)

    def connect(self):
        try:
            self.client.info()
            logging.info('Connected to Qdrant server.')
        except Exception as e:
            logging.error(f'Connection failed: {e}')
            raise

    def create_collection(self, collection_name: str):
        vector_params = models.VectorParams(size=512, distance=models.Distance.COSINE)
        self.client.recreate_collection(name=collection_name, vector_params=vector_params)
        logging.info(f'Collection {collection_name} created.')

    def import_vectorized_data(self, collection_name: str, json_file_path: str):
        import json
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            points = [models.Point(id=item['id'], vector=item['vector']) for item in data]
            self.client.upsert(collection_name=collection_name, points=points)
            logging.info(f'Data imported into collection {collection_name}.')

    def search_by_similarity(self, collection_name: str, query_vector: list):
        results = self.client.search(collection_name=collection_name, query_vector=query_vector)
        logging.info(f'Search results: {results}')
        return results

    def insert_job_data(self, collection_name: str, job_id: str, vector: list):
        self.client.upsert(collection_name=collection_name, points=[models.Point(id=job_id, vector=vector)])
        logging.info(f'Job data for {job_id} inserted.')

    def update_job(self, collection_name: str, job_id: str, update_payload: dict):
        self.client.upsert(collection_name=collection_name, points=[models.Point(id=job_id, payload=update_payload)])
        logging.info(f'Job {job_id} updated.')

    def delete_job(self, collection_name: str, job_id: str):
        self.client.delete(collection_name=collection_name, points=[job_id])
        logging.info(f'Job {job_id} deleted.')