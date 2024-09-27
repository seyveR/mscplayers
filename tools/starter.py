import whisper
import torch
from whisperllm import llama_resp, transcribe_long_audio_with_timestamps
from inference import run_inference
# from langchain_ollama import ChatOllama
# from langchain_core.prompts import PromptTemplate 

video_path = 'D:/r2/tiktok.mp4'
query_text = 'most viral moments more than 10 seconds'

device = "cuda" if torch.cuda.is_available() else "cpu"


model = whisper.load_model("medium", device=device)
audio = whisper.load_audio(video_path)

res_highlights = run_inference(video_path, query_text)
print("Запуск LLM модели")
res_llama = llama_resp(audio, model, device)
print("Модель отработала")

print(res_highlights)
print()
print(res_llama)



