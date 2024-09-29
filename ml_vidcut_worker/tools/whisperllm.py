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

        audio_segment = audio[start_sample:end_sample]
        audio_segment = whisper.pad_or_trim(audio_segment)

        result = model.transcribe(audio_segment)
        text = result['text']
        transcription_with_timestamps.append(f"[{start_time:.2f}-{end_time:.2f}] {text}")

    return transcription_with_timestamps


def llama_resp(audio, model, device, highlights, video_path):
    print("Запуск whisper\n")
    transcribed_text = transcribe_segments_with_timestamps(audio, model, highlights)
    print("Транскрипция завершена")
    print(transcribed_text)
    # extract_audio_segments(video_path, transcribed_text)

    prompt_template = PromptTemplate.from_template(
        """У меня есть транскрипт с ключевыми моментами из видео, и я хочу, чтобы ты описал в 3-5 словах каждый фрагмент отдельно (почему он был выбран).
Таких фрагментов должно быть несколько.
Вот транскрипт:
{script}

Ответ должен быть только в следующем формате: [началофрагмента-конецфрагмента] - краткое обоснование виральности (3-5 слов). Несколько фрагментов.
""")

    script = transcribed_text
    print(prompt_template.format(script=script))

    # Первая модель
    chat = ChatOllama(model='dolphin-llama3', device=device, temperature=0.6)
    chain = prompt_template | chat

    # Вторая модель для оценки
    evaluation_template = PromptTemplate.from_template(
        """Посмотри на пример аннотации, он должен быть выполнен в таком стиле: [началофрагмента-конецфрагмента] - краткое обоснование виральности (3-5 слов).
Аннотация:
{annotation}

Ответь "корректно", если аннотация правильная, или "некорректно", если требуется исправление.
""")
    evaluator = ChatOllama(model='dolphin-llama3', device=device, temperature=0.2)  

    chunks = []
    for chunk in chain.stream({'script': script}):
        chunks.append(chunk.content)
        print(chunk.content, end="", flush=True)
    result = ''.join(chunks)
    print()

    max_attempts = 10 
    attempts = 0

    while attempts < max_attempts:
        evaluation_result = evaluation_template | evaluator
        # evaluation = evaluation_result.invoke({'annotation': result.content})

        eval_chunks = []
        for chunk in evaluation_result.stream({'annotation': result}):
            eval_chunks.append(chunk.content)
            print(chunk.content, end="", flush=True)
        evaluation = ''.join(eval_chunks)
        print()

        if "корректно" in evaluation.lower():
            print("Ответ корректен.")   
            break 
        else:
            print("Ответ некорректен, перегенерация...")
            chunks = []
            for chunk in chain.stream({'script': script}):
                chunks.append(chunk.content)
                print(chunk.content, end="", flush=True)
            result = ''.join(chunks)
            attempts += 1
            print()

#     hashtag = PromptTemplate.from_template(
#         """У меня есть транскрипт с ключевыми моментами из видео, и я хочу, чтобы ты сгенерировал по 4 хэштэга для каждого фрагмента.
# Транскрипт:
# {script}

# Ответ должен содержать только хэштеги и ничего кроме.
# """)

#     script = transcribed_text
#     print(hashtag.format(script=result))

#     # Первая модель
#     chat = ChatOllama(model='dolphin-llama3', device=device, temperature=0.3)
#     chain = prompt_template | chat

#     tags = []
#     for chunk in chain.stream({'script': result}):
#         tags.append(chunk.content)
#         print(chunk.content, end="", flush=True)
#     tag_res = ''.join(tags)
#     print()

    return result

