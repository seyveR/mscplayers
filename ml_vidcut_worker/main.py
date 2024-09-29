import glob
import json
import os

from starlette.websockets import WebSocket

from tools.starter import start_program
from fastapi import FastAPI

from tools.subtitles import start_sub

app = FastAPI()


@app.websocket("/{item_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    item_id: str,
):
    path = '../vidcut/static/upload_videos/'
    full_path = 'D:/r2/R2-Tuning/vidcut/static/upload_videos/' + item_id.replace(".", "cash") + '/'
    await websocket.accept()
    await websocket.send_text(f"Начинаем")
    # path
    query_text = 'most viral moments more than 10 seconds'
    if item_id is None:
        await websocket.close()
        return 0
    flg = await start_program(path, item_id, query_text, websocket)
    await websocket.send_text(f"Накладываем субтитры")
    if flg != 0:
        start_sub(path, item_id)
    await websocket.send_text(f"Завершение")
    result = [f'/static/upload_videos/{ item_id.replace(".","cash") }/' + os.path.basename(i) for i in glob.glob(full_path + 'subtitled_*.mp4')]
    await websocket.send_json(result)
    await websocket.close()
