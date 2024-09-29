import os
import whisper
import subprocess
import soundfile as sf

def transcribe_audio_with_timestamps(video_path, model, chunk_duration=30):
    """Разбивает видео на чанки и транскрибирует каждую часть с временными метками с помощью Whisper."""
    audio = whisper.load_audio(video_path)
    sample_rate = 16000  # Whisper использует фиксированную частоту дискретизации 16 кГц
    duration = len(audio) / sample_rate  # Длительность видео в секундах
    all_transcriptions = []
    
    # Проходим по видео с шагом chunk_duration секунд
    for start in range(0, int(duration), chunk_duration):
        end = min(start + chunk_duration, duration)
        audio_chunk = audio[int(start * sample_rate):int(end * sample_rate)]
        
        # Сохранение чанка во временный аудиофайл
        temp_audio_path = f"temp_chunk_{start}_{end}.wav"
        sf.write(temp_audio_path, audio_chunk, sample_rate)
        
        # Транскрипция файла с использованием Whisper с временными метками
        transcription = model.transcribe(temp_audio_path, language="ru", word_timestamps=True)
        
        # Добавляем временные метки и текст к результату
        for segment in transcription['segments']:
            all_transcriptions.append((segment['start'] + start, segment['end'] + start, segment['text']))
        
        # Удаление временного аудиофайла
        os.remove(temp_audio_path)
    
    return all_transcriptions

def generate_srt_with_timestamps(transcriptions, output_srt_file):
    """Генерация .srt файла с динамическими субтитрами на основе временных меток."""
    with open(output_srt_file, 'w', encoding='utf-8') as srt_file:
        for i, (start, end, text) in enumerate(transcriptions):
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{format_time_srt(start)} --> {format_time_srt(end)}\n")
            srt_file.write(f"{text.strip()}\n\n") 

def format_time_srt(seconds):
    """Форматирование времени для субтитров в формате hh:mm:ss,ms"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

def add_subtitles_to_video(video_path, srt_path, output_video_path):
    """Добавляет субтитры к видео с точными временными метками."""
    # Проверяем, существует ли файл субтитров
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"Файл с субтитрами не найден: {srt_path}")
    
    # Проверяем наличие директории для вывода
    output_dir = os.path.dirname(output_video_path)
    if not os.path.exists(output_dir) and output_dir != '':
        os.makedirs(output_dir)
    
    # Команда для добавления субтитров с позиционированием снизу
    command = [
        'ffmpeg', 
        '-i', video_path, 
        '-vf', f'subtitles={srt_path.replace("\\", "/")}:force_style="Alignment=2"', 
        output_video_path.replace("\\", "/")
    ]
    
    # Запускаем команду
    subprocess.run(command, check=True)

def process_videos_in_output_folder(output_folder, model):
    """Обрабатывает все видео в папке вывода и добавляет субтитры с временными метками."""
    for filename in os.listdir(output_folder):
        if filename.endswith('.mp4'):
            video_path = os.path.join(output_folder, filename)
            srt_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.srt")
            output_video_path = os.path.join(output_folder, f"subtitled_{filename}")

            # Проверяем существование исходного видео
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Видео не найдено: {video_path}")

            # Генерация транскрипции с временными метками и сохранение субтитров
            transcriptions = transcribe_audio_with_timestamps(video_path, model)
            generate_srt_with_timestamps(transcriptions, srt_path)

            # Добавляем субтитры к видео
            add_subtitles_to_video(video_path, srt_path, output_video_path)

def start_sub():
    """Запускает программу обработки видео."""
    output_folder = 'output'
    
    # Создаем директорию, если её нет
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Инициализируем модель Whisper
    model = whisper.load_model("medium")  # Можно использовать модель нужного размера
    
    # Обрабатываем видео в папке вывода
    process_videos_in_output_folder(output_folder, model)

