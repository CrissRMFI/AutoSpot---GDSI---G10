import httpClient from "../../../api/httpClient";

/**
 * Obtiene el historial de conductores con sus alquileres.
 * @param {string|null} usuarioId - UUID del conductor para filtrar (opcional).
 * @returns {Promise<Array>} Lista de conductores con alquileres.
 */
export const getHistorialConductores = async (usuarioId = null) => {
  const params = {};
  if (usuarioId) {
    params.usuario_id = usuarioId;
  }
  const response = await httpClient.get("/admin/historial-conductores", { params });
  return response.data;
};
