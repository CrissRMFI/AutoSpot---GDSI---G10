import httpClient from "../../../api/httpClient";

export const subirFotoVehiculo = async (archivo, lado) => {
  const formData = new FormData();
  formData.append("archivo", archivo);

  const response = await httpClient.post(
    `/upload/foto-vehiculo?lado=${encodeURIComponent(lado)}`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );

  return response.data;
};

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

export const cargarDocumentacionVehiculo = async (
  vehiculoId,
  documentacion,
) => {
  const response = await httpClient.patch(
    `/vehiculos/${vehiculoId}/documentacion`,
    documentacion,
  );

  return response.data;
};

export const listarVehiculosDelPropietario = async (propietarioId) => {
  const response = await httpClient.get(`/usuarios/${propietarioId}/vehiculos`);

  return response.data;
};

export const toggleEstadoVehiculo = async (vehiculoId, disponible) => {
  const response = await httpClient.patch(
    `/vehiculos/${vehiculoId}/disponibilidad`,
    { disponible }
  );

  return response.data;
};

export const getStatusSolicitud = async (vehiculoId) => {
  const response = await httpClient.get(`/vehiculos/${vehiculoId}`);
  return {
    estado_registro: response.data.estado_registro,
    motivo_rechazo: response.data.motivo_rechazo,
  };
};

export const getDetalleVehiculo = async (vehiculoId) => {
  const response = await httpClient.get(`/vehiculos/${vehiculoId}`);
  return response.data;
};

export const actualizarVehiculo = async (vehiculoId, datosVehiculo) => {
  const response = await httpClient.put(
    `/vehiculos/${vehiculoId}`,
    datosVehiculo
  );
  return response.data;
};

export const obtenerCatalogoVehiculos = async () => {
  const response = await httpClient.get(`/vehiculos/catalogo`);
  return response.data;
};

export const getDetalleVehiculoCatalogo = async (vehiculoId) => {
  const response = await httpClient.get(`/vehiculos/catalogo/${vehiculoId}`);
  return response.data;
};

