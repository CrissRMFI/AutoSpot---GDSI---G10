/**
 * Convierte un código de estado a texto presentable, reemplazando los guiones
 * bajos por espacios (ej. "EN_CURSO" → "EN CURSO", "INCIDENTE_REPORTADO" →
 * "INCIDENTE REPORTADO"). Se usa como fallback en toda la app para que ningún
 * estado se muestre con guiones bajos.
 */
export const formatearEstado = (estado) => {
  if (!estado) return "Sin estado";
  return String(estado).replace(/_/g, " ");
};

export const etiquetaEstado = (estado) => {
  const estados = {
    PENDIENTE: "Pendiente",
    PENDIENTE_DOCUMENTACION: "Pendiente de Documentación",
    EN_REVISION: "En Revisión",
    PENDIENTE_REVISION: "En Revisión",
    APROBADO: "Aprobada",
    HABILITADO: "Habilitado",
    RECHAZADO: "Rechazado",
    EXPIRADO: "Expirado",
  };
  return estados[estado] || formatearEstado(estado);
};
