import httpClient from "../../../api/httpClient";

export const getEstacionesActivas = async () => {
  const response = await httpClient.get("/estaciones/");
  return response.data;
};

export const getDetalleEstacion = async (id) => {
  const response = await httpClient.get(`/estaciones/${id}`);
  return response.data;
};
