import httpClient from "../../../api/httpClient";

export const publicarVehiculo = async (propietarioId, datosVehiculo) => {
  const response = await httpClient.post(
    `/usuarios/${propietarioId}/vehiculos`,
    datosVehiculo,
  );

  return response.data;
};
