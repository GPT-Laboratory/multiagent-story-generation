import csv
import os

def save_uploaded_file(upload_folder, file):
    if not file or file.filename == '':
        return None, 'No selected file'
    if not file.filename.endswith('.csv'):
        return None, 'Unsupported file type'

    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    return file_path, None

def parse_csv_to_json(file_path):
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_data = list(csv_reader)  # Convert CSV file content to a list of dictionaries
    os.remove(file_path)  # Optional: remove the file after processing
    return csv_data

def convert_json_to_csv(json_data, csv_file_path):
    # Open the CSV file for writing
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["user_story",'epic', 'BV', 'RR_OE', 'TC', 'JS', 'key','wsjf_factors', 'wsjf_score'])
        writer.writeheader()
        
        for story in json_data:
            # Check for non-ASCII characters and skip if found
            if any(ord(char) > 127 for char in story['user_story']):
                continue
            
            writer.writerow(story)

def convert_json_to_csv_100_dollar(json_data, csv_file_path):
    # Open the CSV file for writing
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["user_story",'epic','key','dollar_allocation'])
        writer.writeheader()
        
        for story in json_data:
            # Check for non-ASCII characters and skip if found
            if any(ord(char) > 127 for char in story['user_story']):
                continue
            
            writer.writerow(story)

def convert_json_to_csv_Ahp(json_data, csv_file_path):
    # Open the CSV file for writing
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["user_story",'epic','key','ID'])
        writer.writeheader()
        
        for story in json_data:
            # Check for non-ASCII characters and skip if found
            if any(ord(char) > 127 for char in story['user_story']):
                continue
            
            writer.writerow(story)