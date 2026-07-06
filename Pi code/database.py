from common import *

def motion_sens(data):
    import cam

    if data['motion_sensor']:
        sensor_value = 'detect'
        event_state = 'on'
        cam.record_video(cam_index=0, duration_sec=10)
    else:
        sensor_value = 'stable'
        event_state = 'off'

    return sensor_value, event_state



def data_scraping(data, datetime, motion_sens):
    all_row = []

    # soil moisture and valve state for each pot
    for i, (s_val, v_state) in enumerate(zip(data['soil_sensors'], data['valves'])):
        all_row.append([datetime[0], datetime[1], f"pot {i+1}", 'soil moisture', s_val, 'valve', "open" if v_state else "close"])
    
    # pump state (general for soil moisture)
    all_row.append([datetime[0], datetime[1], "general", 'soil moisture', 'N/A', 'pump', "on" if data['pump'] else "off"])
    
    # temperature and related events
    all_row.append([datetime[0], datetime[1], "general", 'Air temp', data['temp_sensor'], 'fan', "on" if data['fans'] else "off"])
    all_row.append([datetime[0], datetime[1], "general", 'Air temp', data['temp_sensor'], 'heater', "on" if data['heater'] else "off"])
    
    # LDR and light state
    all_row.append([datetime[0], datetime[1], "general", 'LDR', data['LDR'], 'light', "on" if data['light'] else "off"])
    
    # motion sensor and camera state
    all_row.append([datetime[0], datetime[1], "general", "motion", motion_sens[0], 'camera', motion_sens[1]])

    return all_row



def save_to_csv(data_rows, filename="greenhouse_logs.csv"):
    headers = ['Date', 'Time', 'Zone ID', 'Sensor Type', 'Sensor Value', 'Event Type', 'Event State']

    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(headers)

        writer.writerows(data_rows)
    
    print(f"Done updating {filename} successfully | {date_time()[0]} | {date_time()[1]}")



def data_model_detection(datetime, model_detection):
    all_row = []
    for i, (cams, diseases) in enumerate(model_detection.items()):
        if isinstance(diseases, dict):
            disease_names = ", ".join(diseases.keys())

            all_row.append([datetime[0], datetime[1], f"pot {i+1}", 'AI', 'detect', cams, disease_names ])
            #print(f"{cams}: {disease_names}")    
        else:
            all_row.append([datetime[0], datetime[1], f"pot {i+1}", 'AI', 'stable', cams, diseases])
            #print(f"{cams}: {diseases}")
    
    return all_row
