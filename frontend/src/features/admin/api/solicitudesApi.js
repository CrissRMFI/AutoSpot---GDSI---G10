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
