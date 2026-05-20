import httpClient from "../../../api/httpClient";

export const obtenerDocumentacionHabilitante = async (usuarioId) => {
  const response = await httpClient.get(
    `/usuarios/${usuarioId}/documentacion-habilitante`,
  );
  return response.data;
};

export const registrarDocumentacionHabilitante = async (
  usuarioId,
  documentacion,
) => {
  const response = await httpClient.put(
    `/usuarios/${usuarioId}/documentacion-habilitante`,
    documentacion,
  );
  return response.data;
};

export const actualizarDocumentacionHabilitante = async (
  usuarioId,
  documentacion,
) => {
  const response = await httpClient.put(
    `/usuarios/${usuarioId}/documentacion-habilitante/actualizar`,
    documentacion,
  );
  return response.data;
};
