import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import json

class QdrantManager:
    def __init__(self, host: str = 'localhost', port: int = 6333):
        """Initialize Qdrant manager."""
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "job_knowledge_base"

    def connect(self) -> bool:
        """Connect to Qdrant server."""
        try:
            self.client.get_collections()
            logging.info('✓ Connected to Qdrant server.')
            return True
        except Exception as e:
            logging.error(f'✗ Connection failed: {e}')
            return False

    def create_collection(self, collection_name: str = None, vector_size: int = 384) -> bool:
        """Create a new collection."""
        try:
            if collection_name:
                self.collection_name = collection_name
            
            try:
                self.client.delete_collection(self.collection_name)
            except:
                pass
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logging.info(f'✓ Collection {self.collection_name} created.')
            return True
        except Exception as e:
            logging.error(f'✗ Create collection failed: {e}')
            return False

    def import_vectorized_data(self, json_file_path: str) -> bool:
        """Import vectorized data from JSON."""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            points = []
            for item in data:
                point = PointStruct(
                    id=int(item['job_id']),
                    vector=item['vector'],
                    payload={
                        'title': item.get('title', ''),
                        'company': item.get('company', ''),
                        'location': item.get('location', ''),
                        'salary': item.get('salary', ''),
                        'description': item.get('description', '')
                    }
                )
                points.append(point)
            
            self.client.upsert(collection_name=self.collection_name, points=points)
            logging.info(f'✓ Imported {len(points)} records.')
            return True
        except Exception as e:
            logging.error(f'✗ Import failed: {e}')
            return False

    def search_by_similarity(self, query_vector, limit: int = 10):
        """Search for similar jobs."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            return results
        except Exception as e:
            logging.error(f'✗ Search failed: {e}')
            return []

    def insert_job_data(self, job_data: dict, vector: list) -> bool:
        """Insert job data."""
        try:
            point = PointStruct(
                id=int(job_data.get('job_id', 0)),
                vector=vector,
                payload=job_data
            )
            self.client.upsert(collection_name=self.collection_name, points=[point])
            return True
        except Exception as e:
            logging.error(f'✗ Insert failed: {e}')
            return False

    def update_job(self, job_id: int, updated_payload: dict) -> bool:
        """Update job information."""
        try:
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=updated_payload,
                points_selector=[job_id]
            )
            return True
        except Exception as e:
            logging.error(f'✗ Update failed: {e}')
            return False

    def delete_job(self, job_id: int) -> bool:
        """Delete job."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[job_id]
            )
            return True
        except Exception as e:
            logging.error(f'✗ Delete failed: {e}')
            return False
