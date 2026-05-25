import httpClient from "../../../api/httpClient";

export const getSolicitudesDocumentacion = async () => {
  const response = await httpClient.get("/admin/solicitudes-documentacion");
  return response.data;
};

export const getSolicitudDocumentacionDetalle = async (tipo, recursoId) => {
  const response = await httpClient.get(
    `/admin/solicitudes-documentacion/${tipo}/${recursoId}`,
  );
  return response.data;
};

export const aprobarSolicitud = async (tipo, recursoId) => {
  const response = await httpClient.post(
    `/admin/solicitudes-documentacion/${tipo}/${recursoId}/aprobar`,
  );
  return response.data;
};

export const rechazarSolicitud = async (tipo, recursoId, motivo) => {
  const response = await httpClient.post(
    `/admin/solicitudes-documentacion/${tipo}/${recursoId}/rechazar`,
    { motivo_rechazo: motivo }
  );
  return response.data;
};
