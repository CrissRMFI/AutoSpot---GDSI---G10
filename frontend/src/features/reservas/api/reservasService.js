import httpClient from "../../../api/httpClient";

export const crearReservaConCodigo = async ({
  vehiculoId,
  fechaInicio,
  fechaFin,
}) => {
  const response = await httpClient.post("/alquiler/reservas", {
    vehiculo_id: vehiculoId,
    fecha_inicio: fechaInicio,
    fecha_fin: fechaFin,
  });

  return response.data;
};

export const listarMisReservas = async () => {
  const response = await httpClient.get("/alquiler/reservas");

  return response.data;
};

export const obtenerReservaParaVerificacion = async (reservaId) => {
  const response = await httpClient.get(`/alquiler/reservas/admin/${reservaId}`);

  return response.data;
};

export const verificarCodigoReserva = async (codigoReserva) => {
  const response = await httpClient.post("/alquiler/reservas/verificar-codigo", {
    codigo_reserva: codigoReserva,
  });

  return response.data;
};

export const consultarReservaPorCodigo = async (codigoReserva) => {
  const response = await httpClient.post(
    "/alquiler/reservas/admin/buscar-por-codigo",
    { codigo_reserva: codigoReserva },
  );

  return response.data;
};

export const rechazarReserva = async (reservaId, motivo) => {
  const response = await httpClient.post(
    `/alquiler/reservas/admin/${reservaId}/rechazar`,
    { motivo },
  );

  return response.data;
};
