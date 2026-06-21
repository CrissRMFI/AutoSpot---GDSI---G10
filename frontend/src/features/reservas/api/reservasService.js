import httpClient from "../../../api/httpClient";

export const crearReservaConCodigo = async ({
  vehiculoId,
  fechaFin,
}) => {
  const response = await httpClient.post("/alquiler/reservas", {
    vehiculo_id: vehiculoId,
    fecha_fin: fechaFin,
  });

  return response.data;
};

export const listarMisReservas = async (estado = null) => {
  const response = await httpClient.get("/alquiler/reservas", {
    params: estado ? { estado } : {},
  });

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
    `/alquiler/reservas/admin/${reservaId}/salida`,
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

/**
 * Panel de entregas: reservas por entregar + ya entregadas, ordenadas de
 * más reciente a más antigua. Alimenta la pantalla de Entrega de autos.
 */
export const listarPanelEntregas = async () => {
  const response = await httpClient.get("/alquiler/reservas/admin/entregas");

  return response.data;
};

export const listarRecepcionAutos = async ({ page = 1, size = 10 } = {}) => {
  const response = await httpClient.get("/alquiler/reservas/admin/recepcion", {
    params: { page, size },
  });

  return response.data;
};

/**
 * Reportes criticos — Registra un reporte de falla critica para la reserva.
 * `payload` = { descripcion, fotos: [{ url, descripcion, formato, tamanio_bytes, orden }] }
 */
export const crearReporteIncidencia = async (reservaId, payload) => {
  const response = await httpClient.post(
    `/alquiler/reservas/${reservaId}/reporte`,
    payload,
  );

  return response.data;
};

/** Devuelve el reporte de la reserva si existe (404 si no hay). */
export const obtenerReporteDeReserva = async (reservaId) => {
  const response = await httpClient.get(
    `/alquiler/reservas/${reservaId}/reporte`,
  );

  return response.data;
};

export const enviarValoracion = async (reservaId, puntaje) => {
  const response = await httpClient.post("/valoraciones", {
    reserva_id: reservaId,
    puntaje,
  });

  return response.data;
};

/**
 * US 18C — Registra un testimonio descriptivo sobre un alquiler finalizado.
 * El campo `descripcion` es opcional: puede omitirse o enviarse como null/cadena vacía.
 */
export const enviarTestimonio = async (reservaId, descripcion) => {
  const response = await httpClient.post("/testimonios", {
    reserva_id: reservaId,
    // Normalizar: cadena vacía → null (el backend acepta null)
    descripcion: descripcion?.trim() || null,
  });

  return response.data;
};
