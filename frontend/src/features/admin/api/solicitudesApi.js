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

export const aprobarSolicitudDocumentacion = async (tipo, recursoId) => {
  const response = await httpClient.post(
    `/admin/solicitudes-documentacion/${tipo}/${recursoId}/aprobar`
  );
  return response.data;
};

export const rechazarSolicitudDocumentacion = async (tipo, recursoId, motivoRechazo) => {
  const response = await httpClient.post(
    `/admin/solicitudes-documentacion/${tipo}/${recursoId}/rechazar`,
    { motivo_rechazo: motivoRechazo }
  );
  return response.data;
};
