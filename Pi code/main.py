from common import *
from cam import *
from database import *
from tlg_test import *

#cam.record_video_command(cam_index=0, duration_sec=10, output_file='output.avi')
#Date, Time = date_time()
cam_list = [0, 4]
model_path = "/media/ironwolf/study/هندسة/مشروع التخرج/team task/code/me/best.pt"
model_run_time = 10

ser = serial.Serial('/dev/ttyUSB0', 9600)    


while True:
    Date, Time = date_time()
    config_data = read_greenhouse_config("config.json")

    if config_data:
        farming_group = config_data["farming"]["group"] # e.g., "group1"
        pots_data = config_data["farming"]["pots"]
        light_state = config_data["light"]

    #print(Time)
    if Time == "08:28:00 PM":
        detect = run_smart_multi_greenhouse(cam_indices=cam_list, model_path=model_path, timeout_sec=model_run_time)
        output_detect = data_model_detection(date_time(), detect)
        save_to_csv(output_detect, filename='greenhouse_data.csv')
        time.sleep(1) # عشان ما يكررش في نفس الثانية

    if Time == "11:52:00 PM":
        ser.write(b'r')
        time.sleep(1)
        data = json.dumps(config_data)
        ser.write((data + '\n').encode('utf-8'))
        time.sleep(1)
    
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()

            if not line:
                continue

            data = json.loads(line)
            print(data)

            scraping = data_scraping(data, [Date, Time], motion_sens(data))
            save_to_csv(scraping, filename='greenhouse_data.csv')

    
    except json.JSONDecodeError:
        print("Waiting for valid JSON data...")
    except Exception as e:
        print(f"Error: {e}")
        ser.close()
        break