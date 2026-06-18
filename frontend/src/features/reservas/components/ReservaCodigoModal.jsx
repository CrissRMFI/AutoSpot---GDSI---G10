import { Link } from "react-router-dom";
import { Check, ChevronRight, Clock, KeyRound, X } from "lucide-react";
import { formatearFechaHora, formatearMonto } from "../utils/reservaFormatters";

const ReservaCodigoModal = ({ reserva, verificandoCheckin = false, onClose }) => {
  if (!reserva) return null;

  const vehiculo = reserva.vehiculo;
  const estado = (reserva.estado || "").toUpperCase();
  const checkinEstado = (reserva.checkin?.estado || "").toUpperCase();
  const puedeHacerCheckin = estado === "VERIFICADA";
  const tieneVerificacionRegistrada = Boolean(reserva.codigo_verificado_at);
  const estaRechazada = estado === "RECHAZADA";
  const tituloVehiculo = vehiculo
    ? `${vehiculo.marca} ${vehiculo.modelo}`
    : "Vehículo reservado";

  let chipEncabezadoTexto = "Reserva confirmada";
  let codigoContenedorClass = "border border-autospot-border bg-autospot-cream/40";
  let codigoMensaje = "Válido hasta su primera verificación.";
  let codigoTextClass = "text-autospot-black";

  if (estaRechazada) {
    chipEncabezadoTexto = "Reserva rechazada";
    codigoContenedorClass = "border border-autospot-border bg-autospot-cream/60";
    codigoMensaje = "Esta reserva fue rechazada por el personal de estación.";
    codigoTextClass = "text-autospot-muted line-through decoration-2";
  } else if (puedeHacerCheckin) {
    chipEncabezadoTexto = "Reserva aprobada";
    codigoContenedorClass = "border border-autospot-black bg-autospot-black text-white";
    codigoMensaje = "Código verificado en estación. Ya podés iniciar el check-in.";
    codigoTextClass = "text-white";

    if (verificandoCheckin) {
      codigoMensaje = "Verificando si ya existe un check-in para esta reserva.";
    } else if (checkinEstado === "PENDIENTE") {
      codigoMensaje = "Check-in enviado. Esperá la revisión del administrador.";
    } else if (checkinEstado === "APROBADO") {
      codigoMensaje = "Check-in aprobado. Esperá la entrega del auto en estación.";
    } else if (checkinEstado === "RECHAZADO") {
      codigoMensaje = "Check-in rechazado. Corregí la información y reenvialo.";
    }
  }

  return (
    <div
      className="fixed inset-0 z-[120] flex items-end justify-center bg-autospot-black/70 p-0 backdrop-blur-md sm:items-center sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="reserva-codigo-titulo"
    >
      <div className="flex max-h-[100dvh] w-full flex-col overflow-hidden rounded-t-[28px] bg-autospot-white text-autospot-black shadow-2xl sm:max-h-[calc(100vh-2rem)] sm:max-w-2xl sm:rounded-[28px]">
        <div className="shrink-0 border-b border-autospot-border/70 bg-autospot-white px-5 pb-4 pt-5 sm:border-b-0 sm:px-7 sm:pb-0 sm:pt-7">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-accent">
                {chipEncabezadoTexto}
              </p>
              <h2
                id="reserva-codigo-titulo"
                className="mt-1 font-display text-2xl font-black text-autospot-black"
              >
                {estaRechazada ? "Detalle de la reserva" : "Código de reserva"}
              </h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              aria-label="Cerrar"
              className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-autospot-border bg-white text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
            >
              <X className="h-4 w-4" strokeWidth={2.4} />
            </button>
          </div>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5 sm:px-7">
          <div className={`rounded-2xl p-4 text-center sm:p-5 ${codigoContenedorClass}`}>
            <p className={`flex items-center justify-center gap-2 text-xs font-bold uppercase tracking-[0.1em] ${
              puedeHacerCheckin && !estaRechazada ? "text-white/70" : "text-autospot-muted"
            }`}>
              <KeyRound className="h-3.5 w-3.5" strokeWidth={2.4} />
              {estaRechazada ? "Código de reserva" : "Presentar en estación"}
            </p>
            <p
              className={`mt-3 max-w-full break-all font-display text-[clamp(2rem,12vw,3.4rem)] font-black leading-none sm:break-normal ${codigoTextClass}`}
            >
              {reserva.codigo_reserva}
            </p>
            <p className={`mt-3 text-sm font-semibold ${
              puedeHacerCheckin && !estaRechazada ? "text-white/80" : "text-autospot-muted"
            }`}>
              {codigoMensaje}
            </p>
          </div>

        {puedeHacerCheckin && tieneVerificacionRegistrada && !estaRechazada && (
          <div className="mt-4 flex items-start gap-2 rounded-2xl border border-autospot-border bg-autospot-cream/40 p-4">
            <Check className="mt-0.5 h-4 w-4 shrink-0 text-autospot-black" strokeWidth={2.4} />
            <p className="text-sm font-semibold text-autospot-black">
              Verificación registrada el {formatearFechaHora(reserva.codigo_verificado_at)}.
            </p>
          </div>
        )}

        {estaRechazada && reserva.motivo_rechazo && (
          <div className="mt-4 rounded-2xl border-l-4 border-autospot-accent bg-autospot-cream/60 p-4">
            <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
              Motivo del rechazo
            </p>
            <p className="mt-1 text-sm font-semibold text-autospot-black">
              {reserva.motivo_rechazo}
            </p>
          </div>
        )}

        <dl className="mt-5 space-y-3 text-sm">
          <DatoReserva label="Vehículo" valor={tituloVehiculo} />
          <DatoReserva label="Patente" valor={vehiculo?.patente || "—"} />
          <DatoReserva label="Estación" valor={reserva.estacion_retiro} />
          <DatoReserva
            label="Inicio registrado"
            valor={formatearFechaHora(reserva.fecha_inicio)}
          />
          <DatoReserva
            label="Devolución estimada"
            valor={formatearFechaHora(reserva.fecha_fin)}
          />
          <DatoReserva label="Total" valor={formatearMonto(reserva.monto_total)} />
          <DatoReserva
            label="Estado"
            valor={
              estaRechazada
                ? "Rechazada"
                : verificandoCheckin
                  ? "Verificando check-in"
                  : puedeHacerCheckin
                  ? estadoCheckinReserva(checkinEstado)
                  : estadoReservaPendiente(estado)
            }
          />
        </dl>
        </div>

        <div className="flex shrink-0 flex-col-reverse gap-3 border-t border-autospot-border bg-autospot-white px-5 py-4 sm:flex-row sm:justify-end sm:border-t-0 sm:px-7 sm:pb-7 sm:pt-1">
          <button
            type="button"
            onClick={onClose}
            className="inline-flex w-full justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent sm:w-auto"
          >
            Cerrar
          </button>
          {estaRechazada ? (
            <Link
              to="/catalogo"
              className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
            >
              Ir al catálogo
              <ChevronRight className="h-4 w-4" strokeWidth={2.4} />
            </Link>
          ) : verificandoCheckin ? (
            <button
              type="button"
              disabled
              className="inline-flex w-full cursor-wait items-center justify-center gap-2 rounded-full bg-autospot-black/20 px-5 py-3 text-sm font-bold text-white/70 sm:w-auto"
            >
              <Clock className="h-4 w-4" strokeWidth={2.4} />
              Verificando
            </button>
          ) : puedeHacerCheckin && checkinEstado === "PENDIENTE" ? (
            <button
              type="button"
              disabled
              className="inline-flex w-full cursor-not-allowed items-center justify-center gap-2 rounded-full bg-autospot-black/20 px-5 py-3 text-sm font-bold text-white/70 sm:w-auto"
            >
              <Clock className="h-4 w-4" strokeWidth={2.4} />
              Check-in enviado
            </button>
          ) : puedeHacerCheckin && checkinEstado === "APROBADO" ? (
            <button
              type="button"
              disabled
              className="inline-flex w-full cursor-not-allowed items-center justify-center gap-2 rounded-full bg-autospot-black/20 px-5 py-3 text-sm font-bold text-white/70 sm:w-auto"
            >
              <Check className="h-4 w-4" strokeWidth={2.4} />
              Esperando entrega
            </button>
          ) : puedeHacerCheckin ? (
            <Link
              to={`/usuario/reservas/${reserva.id}/checkin`}
              className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
            >
              <Check className="h-4 w-4" strokeWidth={2.4} />
              {checkinEstado === "RECHAZADO" ? "Corregir check-in" : "Iniciar check-in"}
            </Link>
          ) : (
            <button
              type="button"
              disabled
              className="inline-flex w-full cursor-not-allowed justify-center rounded-full bg-autospot-black/20 px-5 py-3 text-sm font-bold text-white/70 sm:w-auto"
            >
              Esperando verificación
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

const estadoCheckinReserva = (checkinEstado) => {
  if (checkinEstado === "APROBADO") return "Espera de entrega";
  if (checkinEstado === "PENDIENTE") return "Check-in en revisión";
  if (checkinEstado === "RECHAZADO") return "Check-in rechazado";
  return "Falta check-in";
};

const estadoReservaPendiente = (estado) => {
  if (estado === "CONFIRMADA") return "Pendiente de verificación";
  return "Reserva no habilitada para check-in";
};

const DatoReserva = ({ label, valor }) => (
  <div className="grid grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)] items-start gap-3 border-b border-autospot-border/70 pb-2 last:border-b-0 last:pb-0 sm:grid-cols-[1fr_auto]">
    <dt className="min-w-0 text-autospot-muted">{label}</dt>
    <dd className="min-w-0 break-words text-right font-bold text-autospot-black">
      {valor || "—"}
    </dd>
  </div>
);

export default ReservaCodigoModal;
