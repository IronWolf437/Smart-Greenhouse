import cv2
import subprocess
from ultralytics import YOLO
import threading
import time


import serial
import json
import csv
import datetime as dt
import os

#from database import *



""" # استخراج الدقيقة عشان المقارنة
    current_minute = Time[:-3] # هيشيل الثواني ويخليها "09:10 PM"

    # شرط الـ Reset (تحديث الإعدادات)
    if current_minute == "09:10 PM" and not reset_sent:
        print("Sending Reset and Config to ESP...")
        ser.write(b'r')
        time.sleep(1)
        data = json.dumps(config_data)
        ser.write((data + '\n').encode('utf-8'))
        reset_sent = True # نرفع العلم عشان ما يبعتش تاني في نفس الدقيقة
        time.sleep(1)

    # شرط تشغيل الـ AI
    if current_minute == "09:13 PM" and not ai_run_sent:
        print("Running AI Detection...")
        detect = run_smart_multi_greenhouse(cam_indices=cam_list, model_path=model_path, timeout_sec=model_run_time)
        output_detect = data_model_detection(date_time(), detect)
        save_to_csv(output_detect, filename='greenhouse_data.csv')
        ai_run_sent = True
        time.sleep(1)

    # تصفير الأعلام لما الدقيقة تتغير (عشان يشتغلوا تاني يوم)
    if current_minute != "09:10 PM":
        reset_sent = False
    if current_minute != "09:13 PM":
        ai_run_sent = False """


""" while True:
    Date, Time = date_time()
    current_minute = Time[:-3]
    
    # السطر ده هو اللي هيقولنا الحقيقة
    print(f"DEBUG: Current Minute is '{current_minute}' | Waiting for '{reset_time}'") 
    
    config_data = read_greenhouse_config("config.json")
    # ... باقي الكود """



"""     while True:
    Date, Time = date_time()
    
    # التعديل هنا: هناخد الساعة والدقيقة والـ AM/PM بس
    # الـ Time أصلاً بتطلع: 10:01:26 AM
    # إحنا عاوزينها تكون: 10:01 AM
    
    parts = Time.split(" ") # هيقسمها لـ ['10:01:26', 'AM']
    hm = parts[0][:-3]      # هياخد '10:01'
    am_pm = parts[1]        # هياخد 'AM'
    current_minute = f"{hm} {am_pm}" # هتبقى '10:01 AM'

    # اطبع دي عشان تتأكد إنها بقت شبه الـ reset_time بالظبط
    print(f"DEBUG: Now '{current_minute}' | Target '{reset_time}'") """
