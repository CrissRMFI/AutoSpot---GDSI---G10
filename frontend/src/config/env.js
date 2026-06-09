const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || "";

if (!API_BASE_URL) {
  throw new Error("Falta configurar VITE_API_BASE_URL en el archivo .env");
}

export const env = {
  API_BASE_URL,
  VAPID_PUBLIC_KEY,
};
