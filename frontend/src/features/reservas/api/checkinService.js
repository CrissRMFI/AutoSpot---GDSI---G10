import httpClient from "../../../api/httpClient";

export const crearCheckin = async (payload) => {
  const response = await httpClient.post("/checkins", payload);
  return response.data;
};

export const reenviarCheckin = async (checkinId, payload) => {
  const response = await httpClient.put(`/checkins/${checkinId}`, payload);
  return response.data;
};

export const subirFotoCheckin = async (file) => {
  const formData = new FormData();
  formData.append("archivo", file);

  const response = await httpClient.post("/upload/foto-checkin", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const listarCheckinsPendientes = async () => {
  const response = await httpClient.get("/admin/checkins/pendientes");
  return response.data;
};

export const listarCheckins = async () => {
  const response = await httpClient.get("/admin/checkins");
  return response.data;
};

export const obtenerCheckin = async (checkinId) => {
  const response = await httpClient.get(`/admin/checkins/${checkinId}`);
  return response.data;
};

export const aprobarCheckin = async (checkinId) => {
  const response = await httpClient.post(
    `/admin/checkins/${checkinId}/aprobar`,
  );
  return response.data;
};

export const rechazarCheckin = async (checkinId, motivo) => {
  const response = await httpClient.post(
    `/admin/checkins/${checkinId}/rechazar`,
    { motivo },
  );
  return response.data;
};
