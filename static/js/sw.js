// sw.js

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open('video-cache').then(cache => {
            return cache.addAll([
                '/static/videos/cclvideo.mp4',
                // Agrega otros archivos que deseas almacenar en caché aquí
            ]);
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
