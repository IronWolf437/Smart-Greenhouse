from common import *

def record_video(cam_index, duration_sec):
    # 1. إنشاء الفولدرات المتداخلة (surveillance_log/videos)
    # os.path.join بتظبط المسارات تلقائياً على حسب نظام التشغيل (لينكس)
    video_dir = os.path.join('surveillance_log', 'videos')
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    # 2. جلب وتجهيز اسم الفيديو بالوقت والتاريخ
    current_date, current_time = date_time()
    clean_date = str(current_date).replace(" ", "_")
    clean_time = str(current_time).replace(":", "-").replace(" ", "_")
    
    # الاسم النهائي للملف بامتداد mp4
    video_name = f"rec_{clean_date}_{clean_time}.mp4"
    output_path = os.path.join(video_dir, video_name)

    # 3. تشغيل الكاميرا والـ Writer القدام بتوعك زي ما هما
    cam = cv2.VideoCapture(cam_index)
    
    # ملحوظة هندسية: لو شغال على الـ Pi 5 بدون واجهة رسومية (Headless)، 
    # الـ XVID والـ mp4 ممكن يحتاجوا كودك يكون 'mp4v' عشان الـ Container المتوافق.
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    fps = 20.0
    out = cv2.VideoWriter(output_path, fourcc, fps, (640, 480))

    # حساب إجمالي الفريمات المطلوبة
    max_frames = int(duration_sec * fps)
    frames_written = 0

    while frames_written < max_frames:
        isTrue, frame = cam.read()
        if not isTrue:
            break
            
        out.write(frame)
        cv2.imshow('Recording', frame)
        
        frames_written += 1

        if cv2.waitKey(1) & 0xFF == ord('x'):
            break

    cam.release()
    out.release()
    cv2.destroyAllWindows()



def capture_burst_photos(cam_index=0):
    num_images = 5  # تثبيت عدد الصور جوة الدالة بناءً على رأيك المظبوط
    
    # 1. جلب الوقت والتاريخ الحاليين من دالتك
    current_date, _ = date_time()
    clean_date = str(current_date).replace(" ", "_")
    
    # 2. إنشاء الهيكل الشجري للمجلدات المتداخلة: surveillance_log/photos/YYYY-MM-DD
    photo_dir = os.path.join('surveillance_log', 'photos', clean_date)
    if not os.path.exists(photo_dir):
        os.makedirs(photo_dir)
        
    # 3. فتح الكاميرا
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print(f"[ERROR] مش قادر أفتح الكاميرا رقم: {cam_index}")
        return False

    # ترحيب سريع للكاميرا (Warm-up)
    time.sleep(2) 

    for i in range(num_images):
        ret, frame = cap.read()
        if not ret:
            print(f"[ERROR] فشل في التقاط الصورة رقم {i+1}")
            break
            
        # جلب الوقت الحالي لتسمية الصورة بالثانية
        _, current_time = date_time()
        clean_time = str(current_time).replace(":", "-").replace(" ", "_")
        
        # اسم الصورة: time_shot1.jpg
        image_name = f"{clean_time}_shot{i+1}.jpg"
        full_path = os.path.join(photo_dir, image_name)
        
        # حفظ الصورة جوة الفولدر المخصص للتاريخ ده
        cv2.imwrite(full_path, frame)
        print(f"[SUCCESS] تم حفظ لقطة: {full_path}")
        
        # تأخير ثانية واحدة بين اللقطات
        if i < num_images - 1:
            time.sleep(1)
            
    cap.release()
    return True



def record_video_command(cam_index, duration_sec, output_file):
    command = f'ffmpeg -f v4l2 -i /dev/video{cam_index} -t {duration_sec} {output_file}'
    subprocess.run(command, shell=True)





def run_smart_single_camera_greenhouse(cam_index, model_path, timeout_sec=10):
    """
    تحليل الصوبة بكاميرا واحدة مقسمة عرضياً بناءً على كادر الصورة (X-axis)
    لخدمة أصيصين متجاورين فقط (Pot 1 و Pot 2).
    """
    # 1. تحميل الموديل وفتح الكاميرا
    model = YOLO(model_path)
    cap = cv2.VideoCapture(cam_index)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {cam_index}")
        return None

    # دقة الكاميرا الافتراضية
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640

    # 2. حد التقسيم العرضي في المنتصف تماماً (X-axis Calibration)
    # الأصيص اللي على الشمال (Pot 1) | الأصيص اللي على اليمين (Pot 2)
    POT_LIMIT_MID = int(width * 0.50)   # خط المنتصف بالظبط (مثلاً بكسل 320)

    # مخازن تجميع البيانات للأصيصين فقط
    raw_data = {
        "Pot_1": {},  # اليسار (Left)
        "Pot_2": {}   # اليمين (Right)
    }

    print(f"[INFO] Camera started. Resolution: {width}x{height}")
    print(f"[INFO] X-Axis Center Limit -> {POT_LIMIT_MID}")

    start_time = time.time()

    # 3. الـ Main Loop
    while time.time() - start_time < timeout_sec:
        isTrue, frame = cap.read()
        if not isTrue:
            print("Error: Camera disconnected during scanning.")
            break

        # تشغيل الموديل
        results = model(frame, stream=True, conf=0.25, verbose=False)
        
        annotated_frame = frame.copy()

        for r in results:
            boxes = r.boxes
            cls = [int(c) for c in boxes.cls.cpu().numpy()]
            conf = [float(c) for c in boxes.conf.cpu().numpy()]
            xyxy = boxes.xyxy.cpu().numpy()
            names = [r.names[i] for i in cls]

            # رسم المربعات الأصلية من YOLO
            annotated_frame = r.plot()

            # تصنيف كل إصابة بناءً على مكان الـ X (يمين أو شمال خط المنتصف)
            for name, confidence, box in zip(names, conf, xyxy):
                x1, y1, x2, y2 = box
                # حساب منتصف العلبة أفقياً (X_center)
                x_center = (x1 + x2) / 2

                # تحديد الأصيص بناءً على موقع x_center
                if x_center < POT_LIMIT_MID:
                    target_pot = "Pot_1"  # الجزء الأيسر من الكادر
                else:
                    target_pot = "Pot_2"  # الجزء الأيمن من الكادر

                # تخزين البيانات للحساب النهائي
                if name not in raw_data[target_pot]:
                    raw_data[target_pot][name] = {'counts': 0, 'conf_sum': 0}
                raw_data[target_pot][name]['counts'] += 1
                raw_data[target_pot][name]['conf_sum'] += confidence

        # رسم خط توضيحي رأسي واحد في المنتصف يفصل الأصيصين
        cv2.line(annotated_frame, (POT_LIMIT_MID, 0), (POT_LIMIT_MID, height), (0, 255, 255), 2)
        
        # كتابة النصوص فوق المنطقتين
        cv2.putText(annotated_frame, "Pot 1 (Left)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(annotated_frame, "Pot 2 (Right)", (POT_LIMIT_MID + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # عرض الفيديو المباشر
        cv2.imshow('Greenhouse AI Scanner - Single Cam', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('x'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

    # 4. معالجة القرار النهائي للأصيصين
    final_reports = {}
    for pot_name, diseases in raw_data.items():
        pot_decision = {}
        for disease, data in diseases.items():
            avg_conf = data['conf_sum'] / data['counts']
            if avg_conf > 0.40 and data['counts'] > 15:
                pot_decision[disease] = (data['counts'], avg_conf)
        
        final_reports[pot_name] = pot_decision if pot_decision else "Healthy/No Infection"

    return final_reports
