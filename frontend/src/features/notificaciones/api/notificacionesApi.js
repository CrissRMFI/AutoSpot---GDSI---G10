import httpClient from "../../../api/httpClient";

export const getNotificaciones = async () => {
  const response = await httpClient.get("/notificaciones");
  return response.data;
};

export const marcarNotificacionVista = async (notificacionId) => {
  const response = await httpClient.post(
    `/notificaciones/${notificacionId}/vista`,
  );
  return response.data;
};

export const registrarSuscripcionPush = async (suscripcion) => {
  const response = await httpClient.post(
    "/notificaciones/push/suscripciones",
    suscripcion,
  );
  return response.data;
};

export const eliminarSuscripcionPush = async (endpoint) => {
  const response = await httpClient.delete(
    "/notificaciones/push/suscripciones",
    { data: { endpoint } },
  );
  return response.data;
};
