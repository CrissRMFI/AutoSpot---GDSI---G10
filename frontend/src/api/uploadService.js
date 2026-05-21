import httpClient from "./httpClient";

const subirArchivo = async (endpoint, archivo, lado) => {
  const formData = new FormData();
  formData.append("archivo", archivo);

  const response = await httpClient.post(
    `${endpoint}?lado=${encodeURIComponent(lado)}`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );

  return response.data;
};

export const subirFotoDni = (archivo, lado) =>
  subirArchivo("/upload/foto-dni", archivo, lado);

export const subirFotoLicencia = (archivo, lado) =>
  subirArchivo("/upload/foto-licencia", archivo, lado);

export const subirFotoVehiculo = (archivo, lado) =>
  subirArchivo("/upload/foto-vehiculo", archivo, lado);

export const subirFotoDocumentoVehiculo = async (archivo, tipo) => {
  const formData = new FormData();
  formData.append("archivo", archivo);

  const response = await httpClient.post(
    `/upload/foto-documento-vehiculo?tipo=${encodeURIComponent(tipo)}`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );

  return response.data;
};

export const agregarFotoAVehiculo = async (vehiculoId, fotoMetadata) => {
  const response = await httpClient.post(
    `/vehiculos/${vehiculoId}/fotos`,
    fotoMetadata,
  );
  return response.data;
};

export const reemplazarFotoVehiculo = async (vehiculoId, fotoId, fotoMetadata) => {
  const response = await httpClient.put(
    `/vehiculos/${vehiculoId}/fotos/${fotoId}`,
    fotoMetadata,
  );
  return response.data;
};
