import whisper
import torch
from ultralytics import YOLO
from tools.whisperllm import llama_resp
from tools.inference import run_inference
from tools.video_cut import parse_timings, crop_video_to_key_object

def start_program(video_path, query_text):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = whisper.load_model("medium", device=device)
    audio = whisper.load_audio(video_path)

    res_highlights = run_inference(video_path, query_text)
    print(res_highlights)

    print("Запуск LLM модели")
    res_llama = llama_resp(audio, model, device, res_highlights, video_path)
    print("Модель отработала")
    print(res_llama)

    model_yolo = YOLO('yolov8s.pt') 
    model_yolo.to('cpu')

    timings = parse_timings(res_llama)
    for i, (start, end) in enumerate(timings):
        output_file = f"output_video_{i + 1}.mp4" 
        crop_video_to_key_object(video_path, output_file, start, end, model_yolo)