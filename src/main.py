import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from qdrant_client import QdrantClient

# Step 1: Data Loading
# Load data from a CSV file
data = pd.read_csv('data.csv')  # Assume data.csv exists with a 'text' column

# Step 2: Data Filtering
# Filter out entries that are empty or NaN
filtered_data = data[data['text'].notnull() & (data['text'] != '')]

# Step 3: Vectorization
# Using TF-IDF vectorizer to convert text data to vectors
vectorizer = TfidfVectorizer()
vectorized_data = vectorizer.fit_transform(filtered_data['text']).toarray()

# Step 4: Qdrant Client Setup
# Initialize Qdrant client
qdrant_client = QdrantClient(url='http://localhost:6333')

# Step 5: Inserting Vectors into Qdrant
# Create points with vector data
points = [{'id': i, 'vector': vec.tolist()} for i, vec in enumerate(vectorized_data)]
qdrant_client.upsert_points(collection_name='my_collection', points=points)

# Step 6: Search in Qdrant
# Searching for the nearest neighbors
search_result = qdrant_client.search(collection_name='my_collection', query_vector=vectorized_data[0].tolist(), limit=5)

# Print search results
print('Search Results:', search_result)