from common import *


def record_video(cam_index, duration_sec, output_file):
    cam = cv2.VideoCapture(cam_index)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    start_tick = cv2.getTickCount()
    freq = cv2.getTickFrequency()

    while True:
        isTrue, frame = cam.read()
        if not isTrue:
            break
        out.write(frame)
        cv2.imshow('Recording', frame)

        elapsed_time = (cv2.getTickCount() - start_tick) / freq

        if elapsed_time >= duration_sec:
            break
        
        if cv2.waitKey(1) & 0xFF == ord('x'):
            break

    cam.release()
    out.release()
    cv2.destroyAllWindows()





def record_video_command(cam_index, duration_sec, output_file):
    command = f'ffmpeg -f v4l2 -i /dev/video{cam_index} -t {duration_sec} {output_file}'
    subprocess.run(command, shell=True)





def run_smart_multi_greenhouse(cam_indices, model_path, timeout_sec=10):
    frames = {idx: None for idx in cam_indices}
    raw_data = {idx: {} for idx in cam_indices} 
    stop_threads = [False]

    def capture_and_detect(cam_index):
        model = YOLO(model_path)
        cap = cv2.VideoCapture(cam_index)

        if not cap.isOpened():
            raw_data[cam_index] = "OFFLINE" # علامة إن الكاميرا مش موجودة
            return
        
        while not stop_threads[0]:
            isTrue, frame = cap.read()
            if isTrue:
                results = model(frame, stream=True, conf=0.5, verbose=False)
                
                for r in results:
                    frames[cam_index] = r.plot()
                    
                    cls = [int(c) for c in r.boxes.cls.cpu().numpy()]
                    conf = [float(c) for c in r.boxes.conf.cpu().numpy()]
                    names = [r.names[i] for i in cls]

                    for name, confidence in zip(names, conf):
                        if name not in raw_data[cam_index]:
                            raw_data[cam_index][name] = {'counts': 0, 'conf_sum': 0}
                        raw_data[cam_index][name]['counts'] += 1
                        raw_data[cam_index][name]['conf_sum'] += confidence
            else:
                break
        cap.release()

    threads = []
    for idx in cam_indices:
        t = threading.Thread(target=capture_and_detect, args=(idx,))
        t.daemon = True
        t.start()
        threads.append(t)

    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        for idx in cam_indices:
            if frames[idx] is not None:
                cv2.imshow(f'Camera {idx} - Monitoring', frames[idx])

        if cv2.waitKey(1) & 0xFF == ord('x'):
            break
    
    stop_threads[0] = True
    for t in threads:
        t.join()
    cv2.destroyAllWindows()

    final_reports = {}
    for idx in cam_indices:
        # لو الكاميرا كانت أوفلاين من الأول
        if raw_data[idx] == "OFFLINE":
            final_reports[f'Cam_{idx}'] = "Error: Camera Disconnected"
            continue

        cam_decision = {}
        for disease, data in raw_data[idx].items():
            avg_conf = data['conf_sum'] / data['counts']
            if avg_conf > 0.60 and data['counts'] > 30:
                cam_decision[disease] = (data['counts'], avg_conf)
        
        final_reports[f'Cam_{idx}'] = cam_decision if cam_decision else "Healthy/No Infection"

    return final_reports




""" cam_list = [0, 4]
model_path = "/media/ironwolf/study/هندسة/مشروع التخرج/team task/code/me/best.pt"

detect = run_smart_multi_greenhouse(cam_list, model_path, 10)

print(detect) """