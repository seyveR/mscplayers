# Получение виральных клипов 

 Проект содержит два сервиса два основных сервиса:
Django (отображение + запросы на api-modeling)
api-modeling (fast-api + модели)


## api-modeling
Используется для соединения и управления получением нарезок из видео, по сокету начинает выполнение обработки передовая текущии состояния
Для установки api-modeling сервиса выполниете:
- используйте версию python11.9 , создайте env усновите зависимости:
- ```pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121```
- ```pip install --no-cache-dir --upgrade -r /code/requirements.txt```
- ``` uvicorn main:app --port 8000 ```
- 
Обратите внимание на настройку переменной path и full_path в main.py
> path = '../vidcut/static/upload_videos/'
> full_path = 'D:/Studing/videocut/vidcut/static/upload_videos/' + ...

Основной путь для установления socet:
> @app.websocket("/{item_id}/ws")

Со стороны FastApi отрабатывают следующие модели:
-R2 (Highlight Detection), которая выдает тайминги интересных моментов;
-Whisper, которая транскрибирует полученные фрагменты в текст, для дальнейшей обработки;
-LLama (1), обрабатывает текст каждого из фрагментов, для идентификации самых интересных клипов, из предложенных R2;
-LLama (2), обрабатывает текст, полученный LLama(1), для уверенности в том, что полученную ей информацию можно в дальнейшем обработать для работы в Веб-сервисе;
-Yolov8, которая отцентровывает видео относительно "Самого привлекательного объекта" в видеоряде, будь то человек или что-то иное.

Также на FastApi кроме обработки видео происходит и обрезка видео moviepy

## Django
Небольшое приложение с templates и статикой
Используется для:
- фронтенд взаимодейсвия с пользователем 
- бэкенд взаимодейсвия с пользователем
- храенение видео

Для установки Django сервиса выполниете:
- используйте версию python11.9 , создайте env усновите зависимости:
- pip install -r requirements.txt
- python11.9
- ``` python manage.py runserver localhost:80  ```

Используемые urls:
Для начала работы:
> http://127.0.0.1/

Для вызова загрузки файла
> http://127.0.0.1/upload_video/
> method POST

Запрос на api-modeling лежит в файле 
> vidcut\main\templates\main\cutting.html
> var ws = new WebSocket("ws://localhost:8000/{{ video_link }}/ws");

