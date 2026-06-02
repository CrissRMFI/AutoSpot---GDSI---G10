export const etiquetaEstado = (estado) => {
  const estados = {
    PENDIENTE: "Pendiente",
    PENDIENTE_DOCUMENTACION: "Pendiente de Documentación",
    EN_REVISION: "En Revisión",
    PENDIENTE_REVISION: "En Revisión",
    APROBADO: "Aprobada",
    HABILITADO: "Habilitado",
    RECHAZADO: "Rechazado",
  };
  return estados[estado] || estado;
};
