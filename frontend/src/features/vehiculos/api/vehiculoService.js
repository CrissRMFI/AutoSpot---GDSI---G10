import httpClient from "../../../api/httpClient";

export const publicarVehiculo = async (propietarioId, datosVehiculo) => {
  const response = await httpClient.post(
    `/usuarios/${propietarioId}/vehiculos`,
    datosVehiculo,
  );

  return response.data;
};

export const definirPrecioVehiculo = async (vehiculoId, precioPorDia) => {
  const response = await httpClient.patch(`/vehiculos/${vehiculoId}/precio`, {
    precio_por_dia: precioPorDia,
  });

  return response.data;
};

export const listarVehiculosDelPropietario = async (propietarioId) => {
  const response = await httpClient.get(`/usuarios/${propietarioId}/vehiculos`);

  return response.data;
};
