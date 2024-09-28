import whisper
import torch
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate 
from tools.audio_cut import extract_audio_segments

def transcribe_segments_with_timestamps(audio, model, timings):
    transcription_with_timestamps = []

    for segment in timings[1:]:
        start_time, end_time, _ = segment
        duration = end_time - start_time
        
        if duration < 10:
            continue 

        start_sample = int(start_time * whisper.audio.SAMPLE_RATE)
        end_sample = int(end_time * whisper.audio.SAMPLE_RATE)

        # Извлечение отрывка аудио
        audio_segment = audio[start_sample:end_sample]
        audio_segment = whisper.pad_or_trim(audio_segment)

        # Транскрибирование отрывка
        result = model.transcribe(audio_segment)
        text = result['text']
        transcription_with_timestamps.append(f"{text} [{start_time:.2f}-{end_time:.2f}]")

    return transcription_with_timestamps


def llama_resp(audio, model, device, highlights, video_path):
    print("Запуск whisper\n")
    transcribed_text = transcribe_segments_with_timestamps(audio, model, highlights)
    print("Транскрипция завершена")
    print(transcribed_text)
    # extract_audio_segments(video_path, transcribed_text)

    prompt_template = PromptTemplate.from_template(
        """У меня есть транскрипт с ключевыми моментами из видео, и я хочу, чтобы ты описал в 3-5 словах каждый фрагмент отдельно. 
Пожалуйста, не добавляй никаких ненужных пояснений или отказов в ответах. Начало и конец фрагментов бери из транскрипции.

Вот транскрипт:
{script}

Ответ должен быть только в следующем формате: [началофрагмента-конецфрагмента] - аннотация (3-5 слов).
Обработай все фрагменты скрипта обязательно!
""")

    script = transcribed_text

    print(prompt_template.format(script=script))

    chat = ChatOllama(model='dolphin-llama3', device=device, temperature=0.4)

    chain = prompt_template | chat

    result = chain.invoke({'script': script})

    return result.content
