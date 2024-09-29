import moviepy.editor as mp
from pydub import AudioSegment
import numpy as np

def extract_audio_from_video(video_file, audio_file):
    video = mp.VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file)

def get_loud_intervals(audio_file, threshold_multiplier=1.1, min_duration=0.5, merge_distance=2.0):
  
    audio = AudioSegment.from_file(audio_file)
  
    step_duration = 100  
    loudness_values = []
    for i in range(0, len(audio), step_duration):
        segment = audio[i:i+step_duration]
        loudness_values.append(segment.dBFS)
    
    avg_loudness = np.mean(loudness_values)
    threshold = avg_loudness * threshold_multiplier
    
    loud_intervals = []
    start_time = None
    
    for i, loudness in enumerate(loudness_values):
        current_time = i * step_duration / 1000  
        
        if loudness > threshold:
            if start_time is None:
                start_time = current_time  
        else:
            if start_time is not None:
                end_time = current_time  
                
                if end_time - start_time >= min_duration:
                    loud_intervals.append((start_time, end_time))
                start_time = None  
    
    if start_time is not None and (len(audio) / 1000 - start_time >= min_duration):
        loud_intervals.append((start_time, len(audio) / 1000))
    
    merged_intervals = []
    for interval in loud_intervals:
        if not merged_intervals:
            merged_intervals.append(interval)
        else:
            prev_start, prev_end = merged_intervals[-1]
            current_start, current_end = interval
           
            if current_start - prev_end <= merge_distance:
                merged_intervals[-1] = (prev_start, current_end)
            else:
                merged_intervals.append(interval)
    
    return merged_intervals, avg_loudness


def audiotest(video_file, audio_file):
    extract_audio_from_video(video_file, audio_file)

    loud_intervals, avg_loudness = get_loud_intervals(audio_file, min_duration=0.5, merge_distance=2.0)

    print(f"Средняя громкость: {avg_loudness} dBFS")
    print("Промежутки с громкостью выше среднего:")
    for start, end in loud_intervals:
        print(f"С {start:.2f} сек до {end:.2f} сек")
