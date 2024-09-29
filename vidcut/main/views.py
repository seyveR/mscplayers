import base64
import datetime
import hashlib
import time
import urllib.request

import pika
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from .forms import UploadFileForm, UploadRubeLinkForm


def index(request):
    context = {"page": 'index'}
    return render(request, "main/index.html", context)


def register(request):
    context = {"page": 'register'}
    return render(request, "auth/register.html", context)


def login(request):
    context = {"page": 'login'}
    return render(request, "auth/login.html", context)


def forgot(request):
    context = {"page": 'forgot'}
    return render(request, "main/index.html", context)


def handle_uploaded_file(f):
    def compute_file_hash(file, algorithm='sha256'):
        """Compute the hash of a file using the specified algorithm."""
        hash_func = hashlib.new(algorithm)
        for parts in file.chunks():
            hash_func.update(parts)
        return hash_func.hexdigest()

    file_name = compute_file_hash(f) + '.' + f.content_type.replace('video/', '')
    path = "/upload_videos/"
    with open('static/' + path + file_name.lower(), "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path + file_name


def upload_file(request):
    context = {"page": 'index'}
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():
            context['error_upload_file'] = 'Не валидный файл'
            return render(request, "main/index.html", context)
        file = request.FILES["video"]
        print(file, file.content_type)
        if file.content_type not in ['video/mp4', 'video/mov', 'video/avi', 'video/wmv', 'video/WebM', 'video/flv']:
            context['error_upload_file'] = "Формат фидео не: 'mp4', 'mov', 'avi',  'wmv', 'WebM', 'flv'"
            return render(request, "main/index.html", context)
        f_name = handle_uploaded_file(file)
        context['link_static_video'] = f_name
        return render(request, "main/previdcut.html", context)
    else:
        return index(request)


def upload_link_rube(request):
    context = {"page": 'upload_link_rube'}
    if request.method == "POST":
        link_rube = request.POST.get('r_tube_link')
        print(link_rube.find('https://rutube.ru/'))
        if link_rube.find('https://rutube.ru/') == -1:
            context['error_upload_r'] = 'Не валидная ссылка'
            return render(request, "main/index.html", context)
        # filename = 'upload_videos/' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + 'frRuRube.mp4'
        # urllib.request.urlretrieve(link_rube, 'static/' + filename)
        context['link_static_video'] = link_rube
        return render(request, "main/previdcut.html", context)
    else:
        return index(request)


""""""


def models_start_cutting(request):
    """
    В идеале переработать функцию для отправки задачи в очередь
    """
    context = {"page": 'models_start_cutting'}
    if request.method == "POST":
        video_link = request.POST.get('video_link')
        if video_link is None:
            return index(request)
        context['video_link'] = video_link.replace('/static/upload_videos/', '')
        return render(request, "main/cutting.html", context)
    else:
        return index(request)


def answer_vids(request):
    """
    В идеале перераобать функцию для получения факта выполнения задачи из очереди
    """
    time.sleep(20)
    context = {"page": 'models_end_cut'}
    if request.method == "GET":
        video_link = request.GET.get('video_link')
        if video_link is None:
            return index(request)
        context['transcript'] = 'transcript'
        context['timelines'] = 'timelines'
        return JsonResponse(context)
    else:
        return index(request)
