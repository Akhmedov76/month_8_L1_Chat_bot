import csv
import os


class CsvManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def file_exists_and_not_empty(self):
        return os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0

    def read_csv(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)

    def append_csv(self, data):
        with open(self.file_path, 'a', newline='', encoding='utf-8') as file:
            fieldnames = data.keys()
            if self.file_exists_and_not_empty():
                existing_data = self.read_csv()
                if existing_data:
                    fieldnames = existing_data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not self.file_exists_and_not_empty():
                writer.writeheader()
            writer.writerow(data)
