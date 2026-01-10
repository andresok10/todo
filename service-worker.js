/*const CACHE = "web1-v1";
const OFFLINE_FILES = [
    "/",
    "/app.html",
];

self.addEventListener("install", e => {
    e.waitUntil(
        caches.open(CACHE).then(c => c.addAll(OFFLINE_FILES))
    );
});

self.addEventListener("fetch", e => {
    e.respondWith(
        caches.match(e.request).then(r => r || fetch(e.request))
    );
});*/

const CACHE_NAME = "todo-v1";
const OFFLINE_FILES = [
    "/",                // ruta principal
    "/app.html",
    //"/app.py",
    //"/assets/app.js",
    //"/assets/style.css"
    //"/static/style.css" // tu CSS real
];

self.addEventListener("install", e => {
    e.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_FILES)).then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", e => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.map(k => k !== CACHE_NAME ? caches.delete(k) : null))
        )
    );
    self.clients.claim();
});

self.addEventListener("fetch", e => {
    e.respondWith(
        caches.match(e.request).then(r => r || fetch(e.request))
    );
});
