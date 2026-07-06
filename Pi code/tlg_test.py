from common import *

def read_greenhouse_config(file_path="config.json"):
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
