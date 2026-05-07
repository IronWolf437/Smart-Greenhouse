from common import *
import cam

""" def data_scraping(data):
    data = json.loads(data)

    now = dt.datetime.now()
    current_time = now.strftime("%I:%M:%S %p")
    current_day = dt.date.today()

    field = ['date', 'time', 'zone_id', 'sensor_type', 'sensor_value', 'event_type', 'event_state', 'tank_value']

    row = [current_day, current_time, ,value for value in data['soil'], ] """




""" def data_scraping(raw_data, is_cam_running=False):
    if isinstance(raw_data, str):
        data = json.loads(raw_data)
    else:
        data = raw_data

    now = dt.datetime.now()
    current_time = now.strftime("%I:%M:%S %p")
    current_day = dt.date.today()
    tank_str = f"{data['tank']}%"
    
    all_rows = []

    # 1. التربة والمحابس (كل أصيص لوحده)
    for i, (s_val, v_state) in enumerate(zip(data['soil'], data['valve'])):
        all_rows.append([
            current_day, current_time, f"pot {i+1}", 
            "soil moisture", f"{s_val}%", 
            "valve", "open" if v_state else "close", 
            tank_str
        ])

    # 2. المضخة (مرتبطة بالتربة عموماً)
    all_rows.append([
        current_day, current_time, "general", 
        "soil moisture", "N/A", 
        "pump", "on" if data['pump'] else "off", 
        tank_str
    ])

    # 3. الحرارة والرطوبة + (المروحة والدفاية كل واحدة سطر لفصل الـ Event Type)
    temp_val = f"{data['temp']}°C"
    all_rows.append([current_day, current_time, "general", "Air temp", temp_val, "fan", "on" if data['fans'] else "off", tank_str])
    all_rows.append([current_day, current_time, "general", "Air temp", temp_val, "heater", "on" if data['heater'] else "off", tank_str])

    # 4. الإضاءة والكشاف
    all_rows.append([
        current_day, current_time, "general", 
        "LDR", f"{data['LDR']} Lux", 
        "light", "on" if data['light'] else "off", 
        tank_str
    ])

    # 5. الحركة والكاميرا (الـ AI)
    # هنا الـ Sensor Type بيبقى AI والـ Event Type هو الكاميرا
    cam_status = "on" if is_cam_running else "off"
    motion_val = "detect" if data['motion'] else "stable"
    
    all_rows.append([
        current_day, current_time, "general", 
        "AI", motion_val, 
        "camera", cam_status, 
        tank_str
    ])

    return all_rows

# --- تجربة التشغيل ---
sample_data = {
    "soil": [45, 50, 38], "temp": 24, "motion": True, "LDR": 500, "tank": 80,
    "valve": [True, False, True], "pump": True, "fans": False, "heater": True, "light": True
}

# هنا بنشيك هل الكاميرا شغالة (مثلاً لو عامل check على الـ process بتاعة الـ python اللي مشغلة الـ YOLO)
rows = data_scraping(sample_data, is_cam_running=True)

# طباعة الهيدرز للتأكد من الترتيب
headers = ['Date', 'Time', 'Zone ID', 'Sensor Type', 'Sensor Value', 'Event Type', 'Event State', 'Tank']
print(f"{headers[2]:<10} | {headers[3]:<15} | {headers[4]:<12} | {headers[5]:<10} | {headers[6]:<10}")
print("-" * 75)
for r in rows:
    print(f"{r[2]:<10} | {r[3]:<15} | {r[4]:<12} | {r[5]:<10} | {r[6]:<10}")








import json
import datetime as dt
import csv
import os """

""" def save_to_csv(data_rows, filename="greenhouse_logs.csv"):
    # الهيدرز بناءً على الصورة اللي بعتها
    headers = ['Date', 'Time', 'Zone ID', 'Sensor Type', 'Sensor Value', 'Event Type', 'Event State', 'Tank Value']
    
    # التأكد إذا كان الملف موجود قبل كدة ولا لأ عشان محطش الهيدرز كذا مرة
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # كتابة الهيدرز فقط لو الملف لسه جديد
        if not file_exists:
            writer.writerow(headers)
        
        # كتابة كل السطور اللي طلعت من دالة الـ scraping
        writer.writerows(data_rows)
    
    print(f"✅ تم تحديث ملف {filename} بنجاح.")




def data_scraping(raw_data, is_cam_running=False):
    if isinstance(raw_data, str):
        data = json.loads(raw_data)
    else:
        data = raw_data

    now = dt.datetime.now()
    current_time = now.strftime("%I:%M:%S %p")
    current_day = dt.date.today()
    tank_str = f"{data['tank']}%"
    
    all_rows = []

    # 1. التربة والمحابس
    for i, (s_val, v_state) in enumerate(zip(data['soil'], data['valve'])):
        all_rows.append([current_day, current_time, f"pot {i+1}", "soil moisture", f"{s_val}%", "valve", "open" if v_state else "close", tank_str])

    # 2. المضخة
    all_rows.append([current_day, current_time, "general", "soil moisture", "N/A", "pump", "on" if data['pump'] else "off", tank_str])

    # 3. الحرارة (مروحة ودفاية)
    all_rows.append([current_day, current_time, "general", "Air temp", f"{data['temp']}°C", "fan", "on" if data['fans'] else "off", tank_str])
    all_rows.append([current_day, current_time, "general", "Air temp", f"{data['temp']}°C", "heater", "on" if data['heater'] else "off", tank_str])

    # 4. الإضاءة
    all_rows.append([current_day, current_time, "general", "LDR", f"{data['LDR']} Lux", "light", "on" if data['light'] else "off", tank_str])

    # 5. الحركة والكاميرا (الـ AI)
    cam_status = "on" if is_cam_running else "off"
    motion_val = "detect" if data2['motion'] else "stable"
    all_rows.append([current_day, current_time, "general", "AI", motion_val, "camera", cam_status, tank_str])

    return all_rows

# --- مثال لتشغيل السيستم بالكامل ---
sample_data = {
    "soil": [40, 55, 30], "temp": 28, "motion": True, "LDR": 600, "tank": 75,
    "valve": [False, True, False], "pump": True, "fans": True, "heater": False, "light": False
}

# 1. سحب البيانات وتجهيزها
processed_rows = data_scraping(sample_data, is_cam_running=True)

# 2. تخزينها في ملف CSV
save_to_csv(processed_rows) """






def date_time():
    now = dt.datetime.now()
    current_time = now.strftime("%I:%M:%S %p")
    current_date = dt.date.today()
    return current_date, current_time



def motion_sens(data):
    if data['motion_sensor']:
        sensor_value = 'detect'
        event_state = 'on'
        cam.record_video(cam_index=0, duration_sec=10, output_file='test2.mp4')
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






#detect = {'Cam_0': {'green mold': (153, 0.6953658130433824)}, 'Cam_4': 'Error: Camera Disconnected'}


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


""" data = data_model_detection(date_time(), detect)

print(data) """