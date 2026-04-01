"""
Main entry point for the Qdrant Job Data Knowledge Base System.
Handles data loading, filtering, vectorization, and Qdrant integration.
"""

import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_loader import DataLoader
from sentence_transformers import SentenceTransformer

def load_sample_data(json_file: str) -> list:
    """Load sample job data from JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
        return []

def vectorize_jobs(jobs: list, model_name: str = 'all-MiniLM-L6-v2') -> list:
    """Vectorize job descriptions using Sentence Transformers."""
    model = SentenceTransformer(model_name)
    vectorized_jobs = []
    
    print(f"\n🔄 Vectorizing {len(jobs)} job records...")
    
    for idx, job in enumerate(jobs, 1):
        # Combine text fields for vectorization
        text = f"{job.get('title', '')} {job.get('description', '')} {job.get('company', '')}"
        
        # Generate vector
        vector = model.encode(text).tolist()
        
        # Create vectorized job record
        vectorized_job = {
            "job_id": job.get('job_id'),
            "title": job.get('title'),
            "company": job.get('company'),
            "location": job.get('location'),
            "salary": job.get('salary'),
            "description": job.get('description'),
            "vector": vector,
            "vector_dimension": len(vector)
        }
        vectorized_jobs.append(vectorized_job)
        
        if idx % 10 == 0:
            print(f"  ✓ Vectorized {idx} jobs...")
    
    print(f"✅ Vectorization complete: {len(vectorized_jobs)} jobs\n")
    return vectorized_jobs

def save_vectorized_data(vectorized_jobs: list, output_file: str) -> bool:
    """Save vectorized job data to JSON file."""
    try:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(vectorized_jobs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved vectorized data to: {output_file}\n")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}\n")
        return False

def import_to_qdrant(vectorized_data_file: str, 
                     qdrant_host: str = 'localhost',
                     qdrant_port: int = 6333) -> bool:
    """Import vectorized data to Qdrant database."""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
        
        print("🔄 Connecting to Qdrant...")
        client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        # Load vectorized data
        with open(vectorized_data_file, 'r', encoding='utf-8') as f:
            vectorized_jobs = json.load(f)
        
        if not vectorized_jobs:
            print("❌ No vectorized data to import")
            return False
        
        collection_name = "job_knowledge_base"
        vector_size = vectorized_jobs[0].get('vector_dimension', 384)
        
        # Create collection
        print(f"🔄 Creating collection '{collection_name}'...")
        try:
            client.delete_collection(collection_name)
        except:
            pass
        
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        
        # Prepare points
        points = []
        for job in vectorized_jobs:
            point = PointStruct(
                id=int(job['job_id']),
                vector=job['vector'],
                payload={
                    'title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'salary': job.get('salary', ''),
                    'description': job.get('description', '')
                }
            )
            points.append(point)
        
        # Import data
        print(f"🔄 Importing {len(points)} job records to Qdrant...")
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            client.upsert(
                collection_name=collection_name,
                points=batch
            )
            print(f"  ✓ Imported {min(i+batch_size, len(points))}/{len(points)} records")
        
        print(f"✅ Successfully imported to Qdrant!\n")
        return True
        
    except ImportError:
        print("⚠️  qdrant-client not installed. Skipping Qdrant import.")
        return False
    except Exception as e:
        print(f"❌ Error importing to Qdrant: {e}\n")
        return False

def main():
    """Main processing pipeline."""
    print("\n" + "="*60)
    print("🚀 Qdrant Job Data Knowledge Base - Data Processing Pipeline")
    print("="*60 + "\n")
    
    # Configuration
    input_file = 'data/sample_jobs.json'
    output_file = 'data/vectorized_jobs.json'
    qdrant_host = 'localhost'
    qdrant_port = 6333
    
    # Step 1: Load raw data
    print(f"📥 Loading raw job data from: {input_file}")
    jobs = load_sample_data(input_file)
    if not jobs:
        print("❌ Failed to load job data. Exiting.")
        return
    print(f"✅ Loaded {len(jobs)} job records\n")
    
    # Step 2: Vectorize data
    vectorized_jobs = vectorize_jobs(jobs)
    
    # Step 3: Save vectorized data
    if not save_vectorized_data(vectorized_jobs, output_file):
        print("❌ Failed to save vectorized data. Exiting.")
        return
    
    # Step 4: Import to Qdrant
    print("📤 Importing vectorized data to Qdrant database...")
    import_to_qdrant(output_file, qdrant_host, qdrant_port)
    
    print("="*60)
    print("✅ Pipeline completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()