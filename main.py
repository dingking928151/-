import pandas as pd
from qdrant_client import QdrantClient
from sklearn.feature_extraction.text import TfidfVectorizer

# Load job data from CSV
job_data = pd.read_csv('job_data.csv')

# Filter job data based on certain criteria
filtered_jobs = job_data[job_data['location'] == 'Remote']

# Vectorize job descriptions using TF-IDF
vectorizer = TfidfVectorizer()
job_vectors = vectorizer.fit_transform(filtered_jobs['description']).toarray()

# Initialize Qdrant client
client = QdrantClient(host='localhost', port=6333)

# Create a collection in Qdrant
client.recreate_collection(
    collection_name='jobs',
    vector_size=job_vectors.shape[1],
    distance='Cosine'
)

# Prepare data for Qdrant
points = [
    {'id': str(job['id']), 'vector': vector.tolist(), 'payload': job.to_dict()}
    for job, vector in zip(filtered_jobs.to_dict(orient='records'), job_vectors)
]

# Import data into Qdrant
client.upsert(collection_name='jobs', points=points)

# Print the number of imported jobs
print(f'{len(points)} jobs imported into Qdrant.')