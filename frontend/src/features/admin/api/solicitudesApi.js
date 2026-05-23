import httpClient from "../../../api/httpClient";

export const getSolicitudesDocumentacion = async () => {
  const response = await httpClient.get("/admin/solicitudes-documentacion");
  return response.data;
};
