import httpClient from "../../../api/httpClient";

/**
 * Obtiene el historial de autos con sus reservas asociadas.
 * Permite filtrar opcionalmente por estación, fecha y patente.
 */
export const getHistorialAutos = async (params = {}) => {
  const response = await httpClient.get("/admin/historial-autos", { params });
  return response.data;
};

/**
 * Obtiene el detalle de un vehículo con todos sus alquileres
 * (finalizados o en curso). Requiere rol ADMIN.
 */
export const getAlquileresDeAuto = async (vehiculoId) => {
  const response = await httpClient.get(
    `/admin/autos/${vehiculoId}/alquileres`,
  );
  return response.data;
};
