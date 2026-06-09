import { env } from "../../../config/env";
import {
  eliminarSuscripcionPush,
  registrarSuscripcionPush,
} from "../api/notificacionesApi";

const soportaPush = () =>
  typeof window !== "undefined" &&
  "serviceWorker" in navigator &&
  "PushManager" in window &&
  "Notification" in window;

const urlBase64ToUint8Array = (base64String) => {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = `${base64String}${padding}`
    .replace(/-/g, "+")
    .replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; i += 1) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
};

export const registrarPushWeb = async () => {
  if (!soportaPush() || !env.VAPID_PUBLIC_KEY) return null;

  const permiso =
    Notification.permission === "default"
      ? await Notification.requestPermission()
      : Notification.permission;

  if (permiso !== "granted") return null;

  await navigator.serviceWorker.register("/sw.js");
  const serviceWorkerRegistration = await navigator.serviceWorker.ready;
  const existente = await serviceWorkerRegistration.pushManager.getSubscription();
  const subscription =
    existente ||
    (await serviceWorkerRegistration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(env.VAPID_PUBLIC_KEY),
    }));

  await registrarSuscripcionPush(subscription.toJSON());
  return subscription;
};

export const desregistrarPushWeb = async () => {
  if (!soportaPush()) return null;

  const registration = await navigator.serviceWorker.getRegistration();
  const subscription = await registration?.pushManager.getSubscription();
  if (!subscription) return null;

  const { endpoint } = subscription;

  try {
    await eliminarSuscripcionPush(endpoint);
  } catch {
    // El logout vuelve a enviar el endpoint para intentar borrar la fila.
  } finally {
    await subscription.unsubscribe();
  }

  return endpoint;
};
