from common import *
from cam import *
from database import *
from tlg_test import *

import select
import termios
import tty


cam_index = 0
model_path = "best.pt"
model_run_time = 10
manual_trigger_key = "m"

# /dev/ttyUSB0

ser = serial.Serial('/dev/ttyUSB0', 9600)

reset_sent = False
ai_run_sent = False
reset_time = "11:34 AM"
ai_time = "01:39 PM"

stdin_fd = None
stdin_old_settings = None
if os.name == 'posix' and sys.stdin.isatty():
    stdin_fd = sys.stdin.fileno()
    stdin_old_settings = termios.tcgetattr(stdin_fd)
    tty.setcbreak(stdin_fd)


def run_ai_detection_now():
    Date, Time = date_time()
    print(f"Running AI detection manually/timed at {Time}")
    detect = run_smart_single_camera_greenhouse(cam_index=cam_index, model_path=model_path, timeout_sec=model_run_time)
    output_detect = data_model_detection(date_time(), detect)
    save_to_csv(output_detect, filename='greenhouse_data.csv')


def check_manual_trigger():
    if stdin_fd is None:
        return False
    if select.select([sys.stdin], [], [], 0)[0]:
        key = sys.stdin.read(1)
        return key.lower() == manual_trigger_key
    return False


try:
    while True:
        Date, Time = date_time()
        parts = Time.split(" ")  # هيقسمها لـ ['10:01:26', 'AM']
        hm = parts[0][:-3]       # هياخد '10:01'
        am_pm = parts[1]         # هياخد 'AM'
        current_minute = f"{hm} {am_pm}"  # هتبقى '10:01 AM'

        # print(f"DEBUG: Time is '{Time}' | Current Minute is '{current_minute}' | Waiting for '{reset_time}'")

        config_data = read_greenhouse_config("config.json")

        if config_data:
            farming_group = config_data["farming"]["group"]  # e.g., "group1"
            pots_data = config_data["farming"]["pots"]
            light_state = config_data["light"]

        # print(Time)
        if current_minute == reset_time and not reset_sent:
            print("Sending Reset and Config to ESP...")
            ser.write(b'r')
            time.sleep(1)
            data = json.dumps(config_data)
            ser.write((data + '\n').encode('utf-8'))
            reset_sent = True  # نرفع العلم عشان ما يبعتش تاني في نفس الدقيقة
            time.sleep(1)

        if check_manual_trigger():
            print(f"Manual trigger '{manual_trigger_key}' pressed. Running AI detection...")
            run_ai_detection_now()
            time.sleep(1)

        if current_minute == ai_time and not ai_run_sent:
            print("Running AI Detection...")
            run_ai_detection_now()
            ai_run_sent = True
            time.sleep(1)

        # تصفير الأعلام لما الدقيقة تتغير (عشان يشتغلوا تاني يوم)
        if current_minute != reset_time:
            reset_sent = False
        if current_minute != ai_time:
            ai_run_sent = False

        try:
            if ser.in_waiting > 0:
                # هنا ضفنا errors='ignore' عشان لو فيه حرف "هبد" يطنشه ويكمل
                line = ser.readline().decode('utf-8', errors='ignore').strip()

                if not line:
                    continue

                # بنحاول نحول السطر لـ JSON
                data = json.loads(line)
                print("Received Data:", data)

                scraping = data_scraping(data, [Date, Time], motion_sens(data))
                save_to_csv(scraping, filename='greenhouse_data.csv')

        except json.JSONDecodeError:
            # لو السطر واصل مش كامل، هيطبع دي ويكمل اللوب عادي من غير ما يخرج
            print("Waiting for full JSON frame...")
        except Exception as e:
            # هنا بدل ما نقفل البرنامج، هنطبع الخطأ ونخليه يحاول تاني
            print(f"Communication Error: {e}")
            time.sleep(1)
            # ser.close()  <-- شيلنا دي عشان البرنامج ما يقفلش
            # break       <-- وشيلنا دي عشان يفضل شغال
finally:
    if stdin_fd is not None and stdin_old_settings is not None:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, stdin_old_settings)
