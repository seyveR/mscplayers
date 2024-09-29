import re

import moviepy.editor as mp

def parse_timings(annotation_text):
    time_pattern = r"(\d+\.?\d*)-(\d+\.?\d*)"
    matches = re.findall(time_pattern, annotation_text)
    timings = [(float(start), (float(end)) - 1) for start, end in matches]
    return timings

def detect_objects_with_yolov8(frame, model):
    results = model(frame)

    if len(results) == 0:
        return None
    
    for result in results[0].boxes: 
        class_id = int(result.cls)
        confidence = float(result.conf)  
        
        if confidence > 0.5:
            x1, y1, x2, y2 = result.xyxy[0].tolist()  
            center_x = (int(x1) + int(x2)) // 2
            center_y = (int(y1) + int(y2)) // 2
            return center_x, center_y, int(x2 - x1), int(y2 - y1)
    return None


def crop_video_to_key_object(input_video, output_video, start_time, end_time, model):
    clip = mp.VideoFileClip(input_video).subclip(start_time, end_time)

    for frame in clip.iter_frames():
        detected_object = detect_objects_with_yolov8(frame, model)

        if detected_object:
            center_x, center_y, w, h = detected_object

            target_width = 720 
            aspect_ratio = 9 / 16
            crop_height = int(target_width / aspect_ratio) 

            y1 = max(0, center_y - crop_height // 2)
            y2 = min(clip.size[1], center_y + crop_height // 2)
            x1 = max(0, center_x - target_width // 2)
            x2 = min(clip.size[0], center_x + target_width // 2)

            cropped_clip = clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
            cropped_clip = cropped_clip.resize(height=1280) 
            cropped_clip.write_videofile(output_video, codec="libx264")
            break 
