import httpClient from "../../../api/httpClient";

/** Detalle de un reporte (conductor, propietario o admin). */
export const obtenerReporte = async (reporteId) => {
  const response = await httpClient.get(`/reportes/${reporteId}`);

  return response.data;
};

/** Registra la resolucion de un reporte (admin o propietario del vehiculo). */
export const resolverReporte = async (reporteId, resolucionDescripcion) => {
  const response = await httpClient.post(`/reportes/${reporteId}/resolver`, {
    resolucion_descripcion: resolucionDescripcion,
  });

  return response.data;
};

/** Lista de reportes para administracion, opcionalmente filtrada por estado. */
export const listarReportesAdmin = async (params = {}) => {
  const response = await httpClient.get("/admin/reportes", { params });

  return response.data;
};
