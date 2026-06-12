import httpClient from "../../../api/httpClient";

export const obtenerGananciasGenerales = async (propietarioId, periodo) => {
  const response = await httpClient.get(
    `/usuarios/${propietarioId}/ganancias-generales`,
    { params: { periodo } },
  );

  return response.data;
};
