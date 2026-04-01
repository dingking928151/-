import json

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            return data

    def filter_data(self, data, filter_condition):
        return [job for job in data if filter_condition(job)]

    def vectorize_data(self, filtered_data):
        # Placeholder for vectorization logic
        vectorized_data = []
        for job in filtered_data:
            # Apply your vectorization algorithm here
            vectorized_data.append(job)  # Just a placeholder
        return vectorized_data

    def load_filtered_vectorized_data(self, filter_condition):
        raw_data = self.load_data()
        filtered_data = self.filter_data(raw_data, filter_condition)
        return self.vectorize_data(filtered_data)