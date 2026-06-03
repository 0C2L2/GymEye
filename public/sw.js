/* eslint-disable no-restricted-globals */

// Gym Eye does not use an active service worker yet.
// This file exists so older browser registrations stop requesting a missing
// /sw.js and can safely unregister themselves.

self.addEventListener("install", (event) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const registrations = await self.registration.unregister();
      const cacheNames = await caches.keys();

      await Promise.all(cacheNames.map((cacheName) => caches.delete(cacheName)));
      await self.clients.claim();

      return registrations;
    })()
  );
});
