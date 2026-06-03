import type { Metadata } from "next";

import "@/app/globals.css";

export const metadata: Metadata = {
  title: "Gym Eye",
  description: "AI-powered exercise form assistant prototype with live browser camera preview."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function () {
  if (typeof window === "undefined") return;
  if (window.__gymEyeChunkCleanupRan) return;
  window.__gymEyeChunkCleanupRan = true;
  try {
    var marker = "gym-eye-chunk-cleanup-v1";
    var needsReload = !sessionStorage.getItem(marker);
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.getRegistrations().then(function (registrations) {
        return Promise.all(registrations.map(function (registration) {
          return registration.unregister();
        }));
      }).catch(function () {});
    }
    if ("caches" in window) {
      caches.keys().then(function (keys) {
        return Promise.all(keys.map(function (key) {
          return caches.delete(key);
        }));
      }).catch(function () {});
    }
    if (needsReload) {
      sessionStorage.setItem(marker, "1");
      window.location.reload();
    }
  } catch (error) {}
})();`
          }}
        />
        {children}
      </body>
    </html>
  );
}
