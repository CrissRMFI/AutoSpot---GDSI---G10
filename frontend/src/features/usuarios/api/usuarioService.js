import httpClient from "../../../api/httpClient";

export const registrarDatosPersonales = async (usuarioId, datosPersonales) => {
  const response = await httpClient.put(
    `/usuarios/${usuarioId}/datos-personales`,
    datosPersonales,
  );

  return response.data;
};

export const actualizarDatosPersonales = async (usuarioId, datosPersonales) => {
  const response = await httpClient.put(
    `/usuarios/${usuarioId}/datos-personales/actualizar`,
    datosPersonales,
  );

  return response.data;
};
