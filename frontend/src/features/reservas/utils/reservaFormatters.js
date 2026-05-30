export const formatearFechaHora = (valor) => {
  if (!valor) return "—";

  return new Intl.DateTimeFormat("es-AR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(valor));
};

export const formatearMonto = (valor) => {
  const numero = Number(valor);
  if (Number.isNaN(numero)) return `$${valor}`;

  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 0,
  }).format(numero);
};
