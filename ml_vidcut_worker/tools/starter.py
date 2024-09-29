import asyncio
import glob
import os
import time

import whisper
import torch
from ultralytics import YOLO
from tools.whisperllm import llama_resp
from tools.inference import run_inference
from tools.video_cut import parse_timings, crop_video_to_key_object

async def start_program(path, video_path, query_text, websocket):
    output_videos = []
    device = "cuda" if torch.cuda.is_available() else "cpu"
    video_id = video_path.replace('.', 'cash')
    video_path = path + video_path
    model = whisper.load_model("medium", device=device)
    await websocket.send_text(f"Обработка звука")
    await asyncio.sleep(0)
    audio = whisper.load_audio(video_path)
    # if os.path.isdir(path + video_id):
    #     await websocket.send_text(f"Найдено кешированое решение")
    #     await asyncio.sleep(0)
    #     return 0
    res_highlights = run_inference(video_path, query_text)
    print(res_highlights)

    await websocket.send_text(f"Запуск LLM модели")
    await asyncio.sleep(0)
    await websocket.send_text(f"Выполняем поиск интеренсых фрагментов")
    await asyncio.sleep(0)
    res_llama = llama_resp(audio, model, device, res_highlights, video_path)
    await websocket.send_text(f"Модель отработала")
    await asyncio.sleep(0)

    await websocket.send_text(f"Нарезаем видео")
    await asyncio.sleep(0)
    model_yolo = YOLO('yolov8s.pt') 
    model_yolo.to('cpu')
    timings = parse_timings(res_llama)
    print(timings)
    if not os.path.isdir(path + video_id):
        os.mkdir(path + video_id + '/')
    for i, (start, end) in enumerate(timings):
        output_file = f"{path+video_id}/output_video_{i + 1}.mp4"
        crop_video_to_key_object(video_path, output_file, max(start - 1, 0), end - 1, model_yolo)
    return 1