import re
import moviepy.editor as mp
import os
import shutil

def clear_audio_folder(folder):
    """Удаляем все старые аудиофайлы в указанной папке."""
    if os.path.exists(folder):
        shutil.rmtree(folder) 
    os.makedirs(folder)  

def extract_audio_segments(video_file, timings, output_folder='audio'):
    clear_audio_folder(output_folder)
    
    video = mp.VideoFileClip(video_file)
    
    time_pattern = r'\[(\d+\.\d+)-(\d+\.\d+)\]'
    
    for idx, timing in enumerate(timings):
        match = re.search(time_pattern, timing)
        if match:
            start_time = float(match.group(1))  
            end_time = float(match.group(2))  
            
            video_segment = video.subclip(start_time, end_time)
            
            audio_file = os.path.join(output_folder, f'audio_segment_{idx + 1}.mp3')
            video_segment.audio.write_audiofile(audio_file)
            print(f'Аудио сохранено: {audio_file}')