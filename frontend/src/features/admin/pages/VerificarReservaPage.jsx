import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  AlertCircle,
  ArrowLeft,
  Check,
  CheckCircle2,
  Loader2,
  Search,
  X,
} from "lucide-react";
import {
  consultarReservaPorCodigo,
  obtenerReservaParaVerificacion,
  rechazarReserva,
  verificarCodigoReserva,
} from "../../reservas/api/reservasService";
import {
  formatearFechaHora,
  formatearMonto,
} from "../../reservas/utils/reservaFormatters";

const VerificarReservaPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const reservaId = searchParams.get("reservaId");
  const [codigo, setCodigo] = useState("");
  const [detalle, setDetalle] = useState(null);
  const [cargando, setCargando] = useState(Boolean(reservaId));
  const [buscando, setBuscando] = useState(false);
  const [entregando, setEntregando] = useState(false);
  const [error, setError] = useState("");
  const [modalRechazoAbierto, setModalRechazoAbierto] = useState(false);
  const [motivoRechazo, setMotivoRechazo] = useState("");
  const [rechazando, setRechazando] = useState(false);
  const [errorRechazo, setErrorRechazo] = useState("");
  const [resultado, setResultado] = useState(null);

  useEffect(() => {
    if (!reservaId) return;

    let cancelado = false;
    const cargarDetalle = async () => {
      setCargando(true);
      setError("");

      try {
        const data = await obtenerReservaParaVerificacion(reservaId);
        if (cancelado) return;
        setDetalle(data);
        setCodigo(data.codigo_reserva || "");
      } catch (err) {
        if (!cancelado) {
          setError(
            err.response?.data?.detail || "No se pudo cargar la reserva.",
          );
        }
      } finally {
        if (!cancelado) setCargando(false);
      }
    };

    cargarDetalle();

    return () => {
      cancelado = true;
    };
  }, [reservaId]);

  const codigoNormalizado = useMemo(() => codigo.trim(), [codigo]);
  const estadoNormalizado = (detalle?.estado || "").toUpperCase();
  const yaResuelta =
    estadoNormalizado === "VERIFICADA" || estadoNormalizado === "RECHAZADA";
  const puedeRechazar = Boolean(
    detalle?.id && !yaResuelta && !detalle.codigo_verificado_at,
  );

  const handleBuscar = async (event) => {
    event.preventDefault();
    if (!codigoNormalizado) {
      setError("Ingresá un código de reserva.");
      return;
    }

    setBuscando(true);
    setError("");

    try {
      const data = await consultarReservaPorCodigo(codigoNormalizado);
      setDetalle(data);
      setCodigo(data.codigo_reserva || codigoNormalizado);
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo buscar la reserva.");
    } finally {
      setBuscando(false);
    }
  };

  const handleEntregar = async () => {
    if (!detalle?.codigo_reserva) return;

    setEntregando(true);
    setError("");

    try {
      const data = await verificarCodigoReserva(detalle.codigo_reserva);
      setDetalle(data);
      setResultado({
        tipo: "exito",
        titulo: "Verificación realizada",
        mensaje:
          "La reserva fue aprobada. " +
          "Se le notificó al conductor de la aprobación para seguir con el check-in.",
        accionPrimaria: "volver-dashboard",
      });
    } catch (err) {
      setResultado({
        tipo: "error",
        titulo: "No se pudo entregar el auto",
        mensaje:
          err.response?.data?.detail ||
          "Ocurrió un error inesperado y la operación no se procesó. " +
            "Volvé a intentarlo en unos segundos.",
        accionPrimaria: "cerrar",
      });
    } finally {
      setEntregando(false);
    }
  };

  const abrirModalRechazo = () => {
    setMotivoRechazo("");
    setErrorRechazo("");
    setModalRechazoAbierto(true);
  };

  const cerrarModalRechazo = () => {
    if (rechazando) return;
    setModalRechazoAbierto(false);
    setErrorRechazo("");
  };

  const handleConfirmarRechazo = async (event) => {
    event.preventDefault();
    const motivoLimpio = motivoRechazo.trim();
    if (!motivoLimpio) {
      setErrorRechazo("Ingresá el motivo del rechazo.");
      return;
    }
    if (!detalle?.id) return;

    setRechazando(true);
    setErrorRechazo("");

    try {
      const data = await rechazarReserva(detalle.id, motivoLimpio);
      setDetalle(data);
      setModalRechazoAbierto(false);
      setResultado({
        tipo: "exito",
        titulo: "Reserva rechazada",
        mensaje:
          "La reserva fue rechazada con el motivo indicado. " +
          "El conductor recibió la notificación y el vehículo volvió al catálogo.",
        accionPrimaria: "volver-dashboard",
      });
    } catch (err) {
      setErrorRechazo(
        err.response?.data?.detail || "No se pudo rechazar la reserva.",
      );
    } finally {
      setRechazando(false);
    }
  };

  const handleCerrarResultado = () => {
    const accion = resultado?.accionPrimaria;
    setResultado(null);
    if (accion === "volver-dashboard") {
      navigate("/dashboard");
    }
  };

  return (
    <section className="w-full min-w-0 px-5 py-6 sm:px-8 lg:px-10">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase text-autospot-accent">
            US 5R
          </p>
          <h1 className="mt-1 font-display text-3xl font-black text-autospot-black sm:text-4xl">
            Verificar código de reserva
          </h1>
        </div>
        <Link
          to="/dashboard"
          className="inline-flex items-center justify-center gap-2 rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
        >
          <ArrowLeft className="h-4 w-4" strokeWidth={2.4} />
          Volver al dashboard
        </Link>
      </div>

      <div className="grid w-full gap-5 xl:grid-cols-[0.85fr_1.15fr]">
        <form
          onSubmit={handleBuscar}
          className="rounded-[28px] border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-7"
        >
          <label
            htmlFor="codigo-reserva"
            className="text-xs font-bold uppercase text-autospot-muted"
          >
            Código de reserva
          </label>
          <input
            id="codigo-reserva"
            value={codigo}
            onChange={(event) => setCodigo(event.target.value.toUpperCase())}
            className="mt-3 w-full rounded-2xl border border-autospot-border bg-white px-4 py-3 font-display text-2xl font-black text-autospot-black focus:border-autospot-accent focus:outline-none"
            placeholder="AS-000000"
          />

          {error && (
            <div className="mt-4 flex items-start gap-2 rounded-2xl border border-autospot-border bg-autospot-cream/60 p-3 text-sm font-semibold text-autospot-black">
              <AlertCircle
                className="mt-0.5 h-4 w-4 shrink-0 text-autospot-accent"
                strokeWidth={2.4}
              />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={buscando || !codigoNormalizado}
            className={`mt-5 inline-flex w-full items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-bold transition ${
              buscando || !codigoNormalizado
                ? "cursor-not-allowed bg-autospot-accent/40 text-white/70"
                : "bg-autospot-accent text-white hover:bg-[#5a1420]"
            }`}
          >
            {buscando ? (
              <Loader2 className="h-4 w-4 animate-spin" strokeWidth={2.4} />
            ) : (
              <Search className="h-4 w-4" strokeWidth={2.4} />
            )}
            {buscando ? "Buscando..." : "Buscar reserva"}
          </button>
          <p className="mt-3 text-[11px] text-autospot-muted">
            Buscar sólo muestra los datos. El código se marca como usado al
            entregar o rechazar la reserva.
          </p>
        </form>

        <div className="rounded-[28px] border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-7">
          {cargando ? (
            <div className="h-72 animate-pulse rounded-2xl bg-autospot-cream/60" />
          ) : detalle ? (
            <DetalleReservaVerificacion
              detalle={detalle}
              puedeRechazar={puedeRechazar}
              onRechazar={abrirModalRechazo}
              onEntregar={handleEntregar}
              entregando={entregando}
            />
          ) : (
            <div className="flex min-h-72 items-center justify-center rounded-2xl border border-dashed border-autospot-border p-6 text-center">
              <p className="text-sm font-bold text-autospot-muted">
                Ingresá un código para ver los datos de la reserva.
              </p>
            </div>
          )}
        </div>
      </div>

      {modalRechazoAbierto && (
        <ModalRechazarReserva
          motivo={motivoRechazo}
          onMotivoChange={setMotivoRechazo}
          onCancelar={cerrarModalRechazo}
          onConfirmar={handleConfirmarRechazo}
          enviando={rechazando}
          error={errorRechazo}
        />
      )}

      {resultado && (
        <ModalResultado
          resultado={resultado}
          onCerrar={handleCerrarResultado}
        />
      )}
    </section>
  );
};

const ModalResultado = ({ resultado, onCerrar }) => {
  const esExito = resultado.tipo === "exito";
  const Icono = esExito ? CheckCircle2 : AlertCircle;
  const iconoClass = esExito
    ? "bg-autospot-black text-white"
    : "bg-autospot-cream text-autospot-accent border border-autospot-border";
  const ctaLabel =
    resultado.accionPrimaria === "volver-dashboard"
      ? "Volver al dashboard"
      : "Cerrar";

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-autospot-black/65 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="resultado-titulo"
    >
      <div className="w-full max-w-md rounded-[28px] bg-autospot-white p-6 text-autospot-black shadow-2xl sm:p-8">
        <div className="flex flex-col items-center text-center">
          <span
            className={`inline-flex h-14 w-14 items-center justify-center rounded-full ${iconoClass}`}
          >
            <Icono className="h-7 w-7" strokeWidth={2.2} />
          </span>
          <h2
            id="resultado-titulo"
            className="mt-4 font-display text-2xl font-black text-autospot-black"
          >
            {resultado.titulo}
          </h2>
          <p className="mt-2 text-sm font-semibold text-autospot-muted">
            {resultado.mensaje}
          </p>
        </div>
        <button
          type="button"
          onClick={onCerrar}
          autoFocus
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-autospot-black px-5 py-3 text-sm font-bold text-white transition hover:bg-autospot-mid"
        >
          {ctaLabel}
        </button>
      </div>
    </div>
  );
};

const ModalRechazarReserva = ({
  motivo,
  onMotivoChange,
  onCancelar,
  onConfirmar,
  enviando,
  error,
}) => (
  <div
    className="fixed inset-0 z-50 flex items-center justify-center bg-autospot-black/65 p-4 backdrop-blur-sm"
    role="dialog"
    aria-modal="true"
    aria-labelledby="rechazo-reserva-titulo"
  >
    <form
      onSubmit={onConfirmar}
      className="w-full max-w-lg rounded-[28px] bg-autospot-white p-5 text-autospot-black shadow-2xl sm:p-7"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
            Rechazar reserva
          </p>
          <h2
            id="rechazo-reserva-titulo"
            className="mt-1 font-display text-2xl font-black text-autospot-black"
          >
            Indicá el motivo
          </h2>
        </div>
        <button
          type="button"
          onClick={onCancelar}
          aria-label="Cerrar"
          disabled={enviando}
          className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-autospot-border bg-white text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent disabled:cursor-not-allowed disabled:opacity-50"
        >
          <X className="h-4 w-4" strokeWidth={2.4} />
        </button>
      </div>

      <label
        htmlFor="motivo-rechazo"
        className="mt-5 block text-xs font-bold uppercase text-autospot-muted"
      >
        Motivo del rechazo
      </label>
      <textarea
        id="motivo-rechazo"
        rows={4}
        value={motivo}
        onChange={(event) => onMotivoChange(event.target.value)}
        maxLength={500}
        placeholder="Ej: el DNI presentado no coincide con el del conductor."
        className="mt-2 w-full rounded-2xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black focus:border-autospot-accent focus:outline-none"
      />
      <p className="mt-1 text-[11px] text-autospot-muted">
        El conductor verá este motivo en su detalle de reserva.
      </p>

      {error && (
        <div className="mt-4 flex items-start gap-2 rounded-2xl border border-autospot-border bg-autospot-cream/60 p-3 text-sm font-semibold text-autospot-black">
          <AlertCircle
            className="mt-0.5 h-4 w-4 shrink-0 text-autospot-accent"
            strokeWidth={2.4}
          />
          <span>{error}</span>
        </div>
      )}

      <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button
          type="button"
          onClick={onCancelar}
          disabled={enviando}
          className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent disabled:cursor-not-allowed disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={enviando || !motivo.trim()}
          className={`inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-bold transition ${
            enviando || !motivo.trim()
              ? "cursor-not-allowed bg-autospot-black/20 text-white/70"
              : "bg-autospot-black text-white hover:bg-autospot-mid"
          }`}
        >
          {enviando ? (
            <Loader2 className="h-4 w-4 animate-spin" strokeWidth={2.4} />
          ) : (
            <X className="h-4 w-4" strokeWidth={2.4} />
          )}
          {enviando ? "Rechazando..." : "Confirmar rechazo"}
        </button>
      </div>
    </form>
  </div>
);

const DetalleReservaVerificacion = ({
  detalle,
  puedeRechazar,
  onRechazar,
  onEntregar,
  entregando,
}) => {
  const conductor = detalle.conductor || {};
  const vehiculo = detalle.vehiculo || {};
  const nombreConductor = [conductor.nombre, conductor.apellido]
    .filter(Boolean)
    .join(" ");
  const estado = (detalle.estado || "").toUpperCase();
  const estaRechazada = estado === "RECHAZADA";
  const estaVerificada =
    Boolean(detalle.codigo_verificado_at) || estado === "VERIFICADA";

  let badgeIcon = null;
  let badgeClass = "bg-autospot-cream text-autospot-muted";
  let badgeText = "Pendiente";
  if (estaRechazada) {
    badgeClass = "border border-autospot-border bg-white text-autospot-muted";
    badgeText = "Rechazada";
    badgeIcon = <X className="h-3.5 w-3.5" strokeWidth={2.4} />;
  } else if (estaVerificada) {
    badgeClass = "bg-autospot-black text-white";
    badgeText = "Entregada";
    badgeIcon = <Check className="h-3.5 w-3.5" strokeWidth={2.4} />;
  }

  return (
    <div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase text-autospot-accent">
            Reserva {detalle.codigo_reserva}
          </p>
          <h2 className="mt-1 font-display text-2xl font-black text-autospot-black">
            {vehiculo.marca} {vehiculo.modelo}
          </h2>
        </div>
        <span
          className={`inline-flex items-center gap-1.5 justify-center rounded-full px-3 py-1.5 text-xs font-bold ${badgeClass}`}
        >
          {badgeIcon}
          {badgeText}
        </span>
      </div>

      <dl className="mt-5 grid gap-3 text-sm md:grid-cols-2">
        <DatoDetalle
          label="Conductor"
          valor={nombreConductor || conductor.email}
        />
        <DatoDetalle label="DNI" valor={conductor.dni || "Sin registrar"} />
        <DatoDetalle label="Email" valor={conductor.email} />
        <DatoDetalle label="Patente" valor={vehiculo.patente || "—"} />
        <DatoDetalle
          label="Inicio registrado"
          valor={formatearFechaHora(detalle.fecha_inicio)}
        />
        <DatoDetalle
          label="Devolución estimada"
          valor={formatearFechaHora(detalle.fecha_fin)}
        />
        <DatoDetalle label="Estación" valor={detalle.estacion_retiro} />
        <DatoDetalle
          label="Total"
          valor={formatearMonto(detalle.monto_total)}
        />
      </dl>

      {estaRechazada && detalle.motivo_rechazo && (
        <div className="mt-5 rounded-2xl border-l-4 border-autospot-accent bg-autospot-cream/60 p-4 text-sm text-autospot-black">
          <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Motivo del rechazo
          </p>
          <p className="mt-1 font-semibold">{detalle.motivo_rechazo}</p>
        </div>
      )}

      {!estaRechazada && detalle.motivo_bloqueo && (
        <div className="mt-5 flex items-start gap-2 rounded-2xl border border-autospot-border bg-autospot-cream/60 p-4 text-sm font-semibold text-autospot-black">
          <AlertCircle
            className="mt-0.5 h-4 w-4 shrink-0 text-autospot-accent"
            strokeWidth={2.4}
          />
          <span>{detalle.motivo_bloqueo}</span>
        </div>
      )}

      <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        {puedeRechazar && (
          <button
            type="button"
            onClick={onRechazar}
            disabled={entregando}
            className="inline-flex items-center justify-center gap-2 rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-black disabled:cursor-not-allowed disabled:opacity-50"
          >
            <X className="h-4 w-4" strokeWidth={2.4} />
            Rechazar reserva
          </button>
        )}
        {estaRechazada ? (
          <span className="inline-flex items-center justify-center gap-2 rounded-full border border-autospot-border bg-autospot-cream px-5 py-3 text-sm font-bold text-autospot-muted">
            <X className="h-4 w-4" strokeWidth={2.4} />
            Reserva rechazada
          </span>
        ) : estaVerificada ? (
          <span className="inline-flex items-center justify-center gap-2 rounded-full bg-autospot-black px-5 py-3 text-sm font-bold text-white">
            <Check className="h-4 w-4" strokeWidth={2.4} />
            Entregado
          </span>
        ) : (
          <button
            type="button"
            onClick={onEntregar}
            disabled={
              !puedeRechazar || Boolean(detalle.motivo_bloqueo) || entregando
            }
            className={`inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-bold transition ${
              !puedeRechazar || Boolean(detalle.motivo_bloqueo) || entregando
                ? "cursor-not-allowed bg-autospot-black/20 text-white/70"
                : "bg-autospot-black text-white hover:bg-autospot-mid"
            }`}
          >
            {entregando ? (
              <Loader2 className="h-4 w-4 animate-spin" strokeWidth={2.4} />
            ) : (
              <Check className="h-4 w-4" strokeWidth={2.4} />
            )}
            {entregando ? "Confirmando..." : "Confirmar reserva"}
          </button>
        )}
      </div>
    </div>
  );
};

const DatoDetalle = ({ label, valor }) => (
  <div className="rounded-2xl border border-autospot-border bg-white p-4">
    <dt className="text-[11px] font-bold uppercase text-autospot-muted">
      {label}
    </dt>
    <dd className="mt-1 break-words font-bold text-autospot-black">
      {valor || "—"}
    </dd>
  </div>
);

export default VerificarReservaPage;
