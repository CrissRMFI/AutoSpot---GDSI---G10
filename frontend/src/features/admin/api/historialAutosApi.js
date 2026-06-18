import httpClient from "../../../api/httpClient";

/**
 * Obtiene el historial de autos con sus reservas asociadas.
 * Permite filtrar opcionalmente por estación, fecha y patente.
 */
export const getHistorialAutos = async (params = {}) => {
  const response = await httpClient.get("/admin/historial-autos", { params });
  return response.data;
};
