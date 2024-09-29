FROM python:3.11.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
# RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY / /code/app
WORKDIR /code/app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

