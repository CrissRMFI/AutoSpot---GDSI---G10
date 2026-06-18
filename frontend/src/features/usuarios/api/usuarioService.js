import httpClient from "../../../api/httpClient";

export const obtenerDatosPersonales = async (usuarioId) => {
  const response = await httpClient.get(`/usuarios/${usuarioId}/datos-personales`);
  return response.data;
};

export const obtenerDatosPersonalesSiExisten = async (usuarioId) => {
  try {
    return await obtenerDatosPersonales(usuarioId);
  } catch (err) {
    if (err?.response?.status === 404 || err?.status === 404) {
      return null;
    }
    throw err;
  }
};

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
