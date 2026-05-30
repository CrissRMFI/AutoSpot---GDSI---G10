import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Check, ChevronRight, X } from "lucide-react";
import { listarMisReservas } from "../api/reservasService";
import ReservaCodigoModal from "../components/ReservaCodigoModal";
import { formatearFechaHora, formatearMonto } from "../utils/reservaFormatters";

const presentacionEstado = (reserva) => {
  const estado = (reserva.estado || "").toUpperCase();
  if (estado === "RECHAZADA") {
    return {
      cta: "Ver motivo",
      ctaIcon: <ChevronRight className="h-4 w-4" strokeWidth={2.4} />,
      ctaClass: "border border-autospot-border bg-white text-autospot-black",
      etiqueta: "Rechazada",
      etiquetaIcon: <X className="h-3 w-3" strokeWidth={2.4} />,
      etiquetaClass: "border border-autospot-border bg-white text-autospot-muted",
    };
  }
  if (estado === "VERIFICADA" || reserva.codigo_verificado_at) {
    return {
      cta: "Ver reserva",
      ctaIcon: <ChevronRight className="h-4 w-4" strokeWidth={2.4} />,
      ctaClass: "bg-autospot-black !text-white",
      etiqueta: "Aprobada",
      etiquetaIcon: <Check className="h-3 w-3" strokeWidth={2.4} />,
      etiquetaClass: "bg-autospot-black text-white",
    };
  }
  return {
    cta: "Ver código",
    ctaIcon: <ChevronRight className="h-4 w-4" strokeWidth={2.4} />,
    ctaClass: "bg-autospot-accent !text-white",
    etiqueta: "Pendiente",
    etiquetaIcon: null,
    etiquetaClass: "bg-autospot-cream text-autospot-muted",
  };
};

const MisReservasPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const focusId = searchParams.get("focus");
  const [reservas, setReservas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [reservaSeleccionadaId, setReservaSeleccionadaId] = useState(null);
  const [focusConsumido, setFocusConsumido] = useState(false);
  const reservaRefs = useRef({});

  useEffect(() => {
    let cancelado = false;

    const cargarReservas = async () => {
      setCargando(true);
      setError("");

      try {
        const data = await listarMisReservas();
        if (!cancelado) setReservas(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelado) {
          setError(err.response?.data?.detail || "No se pudieron cargar las reservas.");
        }
      } finally {
        if (!cancelado) setCargando(false);
      }
    };

    cargarReservas();

    return () => {
      cancelado = true;
    };
  }, []);

  const focusReserva =
    !cargando && focusId && !focusConsumido
      ? reservas.find((item) => item.id === focusId)
      : undefined;

  const reservaModal =
    reservas.find((item) => item.id === reservaSeleccionadaId) ||
    focusReserva ||
    null;

  useEffect(() => {
    if (!focusReserva) return;
    const nodo = reservaRefs.current[focusReserva.id];
    if (nodo) {
      nodo.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [focusReserva]);

  const cerrarModal = () => {
    setReservaSeleccionadaId(null);
    setFocusConsumido(true);
    if (focusId) {
      const proximo = new URLSearchParams(searchParams);
      proximo.delete("focus");
      setSearchParams(proximo, { replace: true });
    }
  };

  return (
    <>
      <section className="w-full min-w-0">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
              Cliente
            </p>
            <h1 className="font-display text-3xl font-black tracking-[-0.05em] text-autospot-black sm:text-4xl">
              Mis reservas
            </h1>
          </div>
          <Link
            to="/catalogo"
            className="inline-flex justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
          >
            Ir al catálogo
          </Link>
        </div>

        {cargando && (
          <div className="grid gap-4">
            {[0, 1, 2].map((item) => (
              <div
                key={item}
                className="h-36 animate-pulse rounded-2xl border border-autospot-border bg-white/70"
              />
            ))}
          </div>
        )}

        {!cargando && error && (
          <div className="rounded-2xl border border-autospot-border bg-autospot-cream/60 p-5 text-sm font-semibold text-autospot-black">
            {error}
          </div>
        )}

        {!cargando && !error && reservas.length === 0 && (
          <div className="rounded-[28px] border border-autospot-border bg-autospot-white p-8 text-center shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
            <h2 className="font-display text-2xl font-black tracking-[-0.04em] text-autospot-black">
              Todavía no tenés reservas
            </h2>
            <Link
              to="/catalogo"
              className="mt-6 inline-flex rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
            >
              Ver autos disponibles
            </Link>
          </div>
        )}

        {!cargando && !error && reservas.length > 0 && (
          <div className="grid gap-4">
            {reservas.map((reserva) => {
              const vehiculo = reserva.vehiculo;
              const tituloVehiculo = vehiculo
                ? `${vehiculo.marca} ${vehiculo.modelo}`
                : "Vehículo reservado";
              const presentacion = presentacionEstado(reserva);
              const estaFocus = focusId === reserva.id;

              return (
                <button
                  key={reserva.id}
                  ref={(nodo) => {
                    if (nodo) {
                      reservaRefs.current[reserva.id] = nodo;
                    } else {
                      delete reservaRefs.current[reserva.id];
                    }
                  }}
                  type="button"
                  onClick={() => setReservaSeleccionadaId(reserva.id)}
                  className={`grid w-full gap-4 rounded-[24px] border bg-autospot-white p-5 text-left shadow-[0_18px_50px_rgba(15,23,42,0.07)] transition hover:border-autospot-accent sm:grid-cols-[1.3fr_0.9fr_auto] sm:items-center ${
                    estaFocus
                      ? "border-autospot-accent ring-2 ring-autospot-accent/40"
                      : "border-autospot-border"
                  }`}
                >
                  <div>
                    <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-accent">
                      {reserva.codigo_reserva}
                    </p>
                    <h2 className="mt-1 font-display text-xl font-black tracking-[-0.04em] text-autospot-black">
                      {tituloVehiculo}
                    </h2>
                    <p className="mt-2 text-sm text-autospot-muted">
                      {reserva.estacion_retiro}
                    </p>
                  </div>

                  <div className="grid gap-2 text-sm text-autospot-muted sm:grid-cols-2">
                    <DatoLista
                      label="Inicio"
                      valor={formatearFechaHora(reserva.fecha_inicio)}
                    />
                    <DatoLista
                      label="Fin"
                      valor={formatearFechaHora(reserva.fecha_fin)}
                    />
                    <DatoLista
                      label="Total"
                      valor={formatearMonto(reserva.monto_total)}
                    />
                    <div>
                      <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
                        Estado
                      </p>
                      <span
                        className={`mt-1 inline-flex items-center gap-1 rounded-full px-3 py-1 text-[11px] font-bold ${presentacion.etiquetaClass}`}
                      >
                        {presentacion.etiquetaIcon}
                        {presentacion.etiqueta}
                      </span>
                    </div>
                  </div>

                  <span
                    className={`inline-flex items-center justify-center gap-1.5 rounded-full px-4 py-2 text-sm font-bold ${presentacion.ctaClass}`}
                  >
                    {presentacion.cta}
                    {presentacion.ctaIcon}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </section>

      <ReservaCodigoModal reserva={reservaModal} onClose={cerrarModal} />
    </>
  );
};

const DatoLista = ({ label, valor }) => (
  <div>
    <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
      {label}
    </p>
    <p className="font-bold text-autospot-black">{valor || "—"}</p>
  </div>
);

export default MisReservasPage;
