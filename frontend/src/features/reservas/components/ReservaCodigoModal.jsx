import { Link } from "react-router-dom";
import { Check, ChevronRight, KeyRound, X } from "lucide-react";
import { formatearFechaHora, formatearMonto } from "../utils/reservaFormatters";

const ReservaCodigoModal = ({ reserva, onClose }) => {
  if (!reserva) return null;

  const vehiculo = reserva.vehiculo;
  const estado = (reserva.estado || "").toUpperCase();
  const codigoVerificado = Boolean(reserva.codigo_verificado_at) || estado === "VERIFICADA";
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
  } else if (codigoVerificado) {
    chipEncabezadoTexto = "Reserva aprobada";
    codigoContenedorClass = "border border-autospot-black bg-autospot-black text-white";
    codigoMensaje = "Código verificado en estación. Ya podés iniciar el check-in.";
    codigoTextClass = "text-white";
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-autospot-black/65 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="reserva-codigo-titulo"
    >
      <div className="w-full max-w-2xl rounded-[28px] bg-autospot-white p-5 text-autospot-black shadow-2xl sm:p-7">
        <div className="flex items-start justify-between gap-4">
          <div>
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
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-autospot-border bg-white text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
          >
            <X className="h-4 w-4" strokeWidth={2.4} />
          </button>
        </div>

        <div className={`mt-5 rounded-2xl p-5 text-center ${codigoContenedorClass}`}>
          <p className={`flex items-center justify-center gap-2 text-xs font-bold uppercase tracking-[0.1em] ${
            codigoVerificado && !estaRechazada ? "text-white/70" : "text-autospot-muted"
          }`}>
            <KeyRound className="h-3.5 w-3.5" strokeWidth={2.4} />
            {estaRechazada ? "Código de reserva" : "Presentar en estación"}
          </p>
          <p
            className={`mt-2 max-w-full overflow-x-auto whitespace-nowrap font-display text-[clamp(1.9rem,7vw,3.4rem)] font-black ${codigoTextClass}`}
          >
            {reserva.codigo_reserva}
          </p>
          <p className={`mt-3 text-sm font-semibold ${
            codigoVerificado && !estaRechazada ? "text-white/80" : "text-autospot-muted"
          }`}>
            {codigoMensaje}
          </p>
        </div>

        {codigoVerificado && !estaRechazada && (
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
            label="Inicio"
            valor={formatearFechaHora(reserva.fecha_inicio)}
          />
          <DatoReserva
            label="Fin"
            valor={formatearFechaHora(reserva.fecha_fin)}
          />
          <DatoReserva label="Total" valor={formatearMonto(reserva.monto_total)} />
          <DatoReserva
            label="Estado"
            valor={
              estaRechazada
                ? "Rechazada"
                : codigoVerificado
                  ? "Aprobada"
                  : "Pendiente de verificación"
            }
          />
        </dl>

        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onClose}
            className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
          >
            Cerrar
          </button>
          {estaRechazada ? (
            <Link
              to="/catalogo"
              className="inline-flex items-center justify-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
            >
              Ir al catálogo
              <ChevronRight className="h-4 w-4" strokeWidth={2.4} />
            </Link>
          ) : codigoVerificado ? (
            <Link
              to={`/usuario/reservas/${reserva.id}/checkin`}
              className="inline-flex items-center justify-center gap-2 rounded-full bg-autospot-black px-5 py-3 text-sm font-bold !text-white transition hover:bg-autospot-mid"
            >
              <Check className="h-4 w-4" strokeWidth={2.4} />
              Iniciar check-in
            </Link>
          ) : (
            <button
              type="button"
              disabled
              className="inline-flex cursor-not-allowed justify-center rounded-full bg-autospot-black/20 px-5 py-3 text-sm font-bold text-white/70"
            >
              Check-in
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

const DatoReserva = ({ label, valor }) => (
  <div className="flex items-center justify-between gap-3 border-b border-autospot-border/70 pb-2 last:border-b-0 last:pb-0">
    <dt className="text-autospot-muted">{label}</dt>
    <dd className="text-right font-bold text-autospot-black">{valor || "—"}</dd>
  </div>
);

export default ReservaCodigoModal;
