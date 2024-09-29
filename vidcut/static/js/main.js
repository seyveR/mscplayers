document.addEventListener('DOMContentLoaded', function() {
    const downloadButton = document.querySelector('.custom-download');
    downloadButton.addEventListener('click', downloadVideo);
});

function downloadVideo() {
    const videoSource = document.querySelector('.video-block video source');

    // Проверка, что элемент найден
    if (!videoSource) {
        console.error('Видео элемент не найден.');
        return;
    }

    const videoUrl = videoSource.src;

    // Проверка URL видео
    if (!videoUrl) {
        console.error("URL видео не найден.");
        return;
    }

    // Создание ссылки для загрузки
    const a = document.createElement('a');
    a.href = videoUrl;
    a.download = 'video.mp4';

    // Добавляем ссылку и кликаем по ней
    document.body.appendChild(a);
    a.click();
    
    // Удаляем ссылку после клика
    document.body.removeChild(a);
}

console.log('Video URL:', videoUrl);