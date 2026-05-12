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
    


""" config_data = read_greenhouse_config("config.json")

if config_data:
    farming_group = config_data["farming"]["group"] # e.g., "group1"
    pots_data = config_data["farming"]["pots"]
    light_state = config_data["light"]
    
    print(f"Farming group: {farming_group}")
    print(f"Pots data: {pots_data}")
    print(f"Light state: {light_state}") """
