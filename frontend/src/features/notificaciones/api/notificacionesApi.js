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
