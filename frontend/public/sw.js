self.addEventListener("push", (event) => {
  let payload;

  try {
    payload = event.data ? event.data.json() : {};
  } catch {
    payload = {
      title: "AutoSpot",
      body: event.data ? event.data.text() : "Tienes una nueva notificacion.",
    };
  }

  const title = payload.title || "AutoSpot";
  const data = payload.data || {};
  const options = {
    body: payload.body || "Tienes una nueva notificacion.",
    icon: "/favicon.svg",
    badge: "/favicon.svg",
    data: {
      url: data.url || "/dashboard",
      ...data,
    },
    tag: data.recurso_id || data.tipo || "autospot-notificacion",
    renotify: false,
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const targetUrl = new URL(
    event.notification.data?.url || "/dashboard",
    self.location.origin,
  ).href;

  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true })
      .then((clientsList) => {
        const client = clientsList.find((item) => item.url === targetUrl);
        if (client) return client.focus();
        return self.clients.openWindow(targetUrl);
      }),
  );
});
