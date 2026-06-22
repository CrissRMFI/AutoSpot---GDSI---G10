import httpClient from "../../../api/httpClient";

export const listarIncidentes = async (filtros = {}) => {
  const params = new URLSearchParams();
  if (filtros.codigo_reserva) params.append("codigo_reserva", filtros.codigo_reserva);
  if (filtros.conductor) params.append("conductor", filtros.conductor);
  if (filtros.fecha) params.append("fecha", filtros.fecha);
  if (filtros.patente) params.append("patente", filtros.patente);

  const url = `/admin/incidentes?${params.toString()}`;
  const response = await httpClient.get(url);
  return response.data;
};

export const obtenerIncidenteDetalle = async (id) => {
  const response = await httpClient.get(`/admin/incidentes/${id}`);
  return response.data;
};
