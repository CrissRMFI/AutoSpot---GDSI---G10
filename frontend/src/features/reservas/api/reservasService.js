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

export const listarMisAlquileres = async ({ page = 1, size = 10 } = {}) => {
  const response = await httpClient.get("/alquiler/mis-alquileres", {
    params: { page, size },
  });

  return response.data;
};

export const obtenerMiAlquiler = async (reservaId) => {
  const response = await httpClient.get(`/alquiler/reservas/${reservaId}`);

  return response.data;
};

export const entregarAuto = async (reservaId) => {
  const response = await httpClient.post(`/alquiler/reservas/${reservaId}/entregar`);

  return response.data;
};

export const obtenerCheckoutDeReserva = async (reservaId) => {
  const response = await httpClient.get(`/alquiler/reservas/${reservaId}/checkout`);

  return response.data;
};

export const confirmarCheckout = async (checkoutId) => {
  const response = await httpClient.post(`/alquiler/checkouts/${checkoutId}/confirmar`);

  return response.data;
};

export const rechazarCheckout = async (checkoutId, motivo) => {
  const response = await httpClient.post(`/alquiler/checkouts/${checkoutId}/rechazar`, {
    motivo,
  });

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

export const registrarSalida = async (reservaId) => {
  const response = await httpClient.post(
    `/alquiler/reservas/admin/${reservaId}/registrar-salida`,
  );

  return response.data;
};

export const registrarEntrada = async (reservaId) => {
  const response = await httpClient.post(
    `/alquiler/reservas/admin/${reservaId}/registrar-entrada`,
  );

  return response.data;
};

export const listarReservasParaEntregar = async () => {
  const response = await httpClient.get("/alquiler/reservas/admin/para-entregar");

  return response.data;
};

export const listarRecepcionAutos = async ({ page = 1, size = 10 } = {}) => {
  const response = await httpClient.get("/alquiler/reservas/admin/recepcion", {
    params: { page, size },
  });

  return response.data;
};
