import json
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class DataLoader:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.data = self.load_data()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def load_data(self) -> List[Dict[str, Any]]:
        """Load job data from JSON file."""
        with open(self.json_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def filter_jobs(self, location=None, min_salary=None, keywords=None) -> List[Dict]:
        """Filter jobs based on criteria."""
        filtered_jobs = self.data
        if location:
            filtered_jobs = [job for job in filtered_jobs 
                           if location.lower() in job.get('location', '').lower()]
        if min_salary:
            filtered_jobs = [job for job in filtered_jobs 
                           if self._extract_salary(job.get('salary', '')) >= min_salary]
        if keywords:
            filtered_jobs = [job for job in filtered_jobs 
                           if any(kw.lower() in job.get('description', '').lower() for kw in keywords)]
        return filtered_jobs

    def _extract_salary(self, salary_str: str) -> int:
        """Extract salary value from string."""
        import re
        numbers = re.findall(r'\d+', salary_str.replace(',', ''))
        return int(numbers[0]) // 1000 if numbers and int(numbers[0]) > 10000 else (int(numbers[0]) if numbers else 0)

    def vectorize_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Vectorize jobs and return with vector data."""
        vectorized_jobs = []
        for job in jobs:
            text = f"{job.get('title', '')} {job.get('description', '')} {job.get('company', '')}"
            vector = self.model.encode(text).tolist()
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
        return vectorized_jobs

    def export_to_json(self, vectorized_jobs: List[Dict], export_path: str):
        """Export vectorized jobs to JSON file."""
        with open(export_path, 'w', encoding='utf-8') as file:
            json.dump(vectorized_jobs, file, ensure_ascii=False, indent=2)

    def process_pipeline(self, location=None, min_salary=None, keywords=None, 
                        export_path='data/vectorized_jobs.json'):
        """Complete processing pipeline."""
        filtered_jobs = self.filter_jobs(location, min_salary, keywords)
        vectorized_jobs = self.vectorize_jobs(filtered_jobs)
        self.export_to_json(vectorized_jobs, export_path)
        return vectorized_jobs
