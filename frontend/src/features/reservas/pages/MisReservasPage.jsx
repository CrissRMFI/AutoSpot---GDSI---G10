import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Check, ChevronLeft, ChevronRight, Clock, X } from "lucide-react";
import { listarMisReservas } from "../api/reservasService";
import {
  obtenerEstadoCheckinReservaRecordado,
  obtenerMiCheckinPorReserva,
} from "../api/checkinService";
import ReservaCodigoModal from "../components/ReservaCodigoModal";
import EstacionInfoModal from "../components/EstacionInfoModal";
import { formatearFechaHora, formatearMonto } from "../utils/reservaFormatters";

const PAGE_SIZE = 5;
const ESTADOS_PENDIENTES_VERIFICACION = new Set(["CONFIRMADA"]);

const estadoReserva = (reserva) => (reserva.estado || "").toUpperCase();

const puedeHacerCheckin = (reserva) => estadoReserva(reserva) === "VERIFICADA";

const estaPendienteDeVerificacion = (reserva) =>
  ESTADOS_PENDIENTES_VERIFICACION.has(estadoReserva(reserva));

const checkinRecordado = (reservaId) => {
  const estado = (obtenerEstadoCheckinReservaRecordado(reservaId) || "").toUpperCase();
  return estado ? { estado } : null;
};

const prioridadReserva = (reserva) => {
  const estado = estadoReserva(reserva);
  const checkinEstado = (reserva.checkin?.estado || "").toUpperCase();

  if (puedeHacerCheckin(reserva)) {
    if (!checkinEstado || checkinEstado === "RECHAZADO") return 0;
    if (checkinEstado === "PENDIENTE") return 1;
    if (checkinEstado === "APROBADO") return 2;
    return 3;
  }

  if (estaPendienteDeVerificacion(reserva)) return 3;
  if (estado === "RECHAZADA") return 5;
  return 4;
};

const ordenarReservas = (reservas) =>
  [...reservas].sort((a, b) => {
    const prioridad = prioridadReserva(a) - prioridadReserva(b);
    if (prioridad !== 0) return prioridad;
    return (a._ordenOriginal ?? 0) - (b._ordenOriginal ?? 0);
  });

const presentacionEstado = (reserva) => {
  const estado = estadoReserva(reserva);
  const checkinEstado = (reserva.checkin?.estado || "").toUpperCase();

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
  if (puedeHacerCheckin(reserva)) {
    if (checkinEstado === "APROBADO") {
      return {
        cta: "Ver reserva",
        ctaIcon: <ChevronRight className="h-4 w-4" strokeWidth={2.4} />,
        ctaClass: "bg-autospot-black !text-white",
        etiqueta: "Espera de entrega",
        etiquetaIcon: <Check className="h-3 w-3" strokeWidth={2.4} />,
        etiquetaClass: "bg-[#f0fdf4] text-[#166534]",
      };
    }

    if (checkinEstado === "PENDIENTE") {
      return {
        cta: "Ver reserva",
        ctaIcon: <ChevronRight className="h-4 w-4" strokeWidth={2.4} />,
        ctaClass: "bg-autospot-black !text-white",
        etiqueta: "Check-in en revisión",
        etiquetaIcon: <Clock className="h-3 w-3" strokeWidth={2.4} />,
        etiquetaClass: "bg-[#fef3c7] text-[#92400e]",
      };
    }

    if (checkinEstado === "RECHAZADO") {
      return {
        cta: "Corregir check-in",
        ctaIcon: <ChevronRight className="h-4 w-4" strokeWidth={2.4} />,
        ctaClass: "bg-autospot-accent !text-white",
        etiqueta: "Check-in rechazado",
        etiquetaIcon: <X className="h-3 w-3" strokeWidth={2.4} />,
        etiquetaClass: "bg-[#fef2f2] text-[#b42318]",
      };
    }

    return {
      cta: "Iniciar check-in",
      ctaIcon: <ChevronRight className="h-4 w-4" strokeWidth={2.4} />,
      ctaClass: "bg-autospot-accent !text-white",
      etiqueta: "Falta check-in",
      etiquetaIcon: <Check className="h-3 w-3" strokeWidth={2.4} />,
      etiquetaClass: "bg-autospot-black text-white",
    };
  }

  if (estaPendienteDeVerificacion(reserva)) {
    return {
      cta: "Ver código",
      ctaIcon: <ChevronRight className="h-4 w-4" strokeWidth={2.4} />,
      ctaClass: "bg-autospot-accent !text-white",
      etiqueta: "Pendiente de verificación",
      etiquetaIcon: <Clock className="h-3 w-3" strokeWidth={2.4} />,
      etiquetaClass: "bg-[#fef3c7] text-[#92400e]",
    };
  }

  return {
    cta: "Ver reserva",
    ctaIcon: <ChevronRight className="h-4 w-4" strokeWidth={2.4} />,
    ctaClass: "border border-autospot-border bg-white text-autospot-black",
    etiqueta: etiquetaEstadoReserva(estado),
    etiquetaIcon: null,
    etiquetaClass: "bg-autospot-cream text-autospot-muted",
  };
};

const etiquetaEstadoReserva = (estado) => {
  const etiquetas = {
    EN_CURSO: "Alquiler en curso",
    ENTREGA_SOLICITADA: "Entrega solicitada",
    DEVUELTO: "Devuelto",
    CHECKOUT_PENDIENTE: "Checkout pendiente",
    FINALIZADA: "Finalizada",
  };

  return etiquetas[estado] || "Reserva";
};

const MisReservasPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const focusId = searchParams.get("focus");
  const pageParam = Number(searchParams.get("page") || "1");
  const paginaActual = Number.isFinite(pageParam) && pageParam > 0 ? pageParam : 1;
  const [reservas, setReservas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [reservaSeleccionadaId, setReservaSeleccionadaId] = useState(null);
  const [reservasVerificandoCheckin, setReservasVerificandoCheckin] = useState(
    () => new Set(),
  );
  const [focusConsumido, setFocusConsumido] = useState(false);
  const reservaRefs = useRef({});

  useEffect(() => {
    let cancelado = false;

    const cargarReservas = async () => {
      setCargando(true);
      setError("");

      try {
        const data = await listarMisReservas();
        const items = Array.isArray(data) ? data : [];
        const enriquecidas = await Promise.all(
          items.map(async (reserva, index) => {
            if (!puedeHacerCheckin(reserva)) {
              return { ...reserva, _ordenOriginal: index };
            }

            try {
              const checkin = await obtenerMiCheckinPorReserva(reserva.id);
              return { ...reserva, checkin, _ordenOriginal: index };
            } catch (err) {
              if (err.response?.status === 404) {
                return {
                  ...reserva,
                  checkin: checkinRecordado(reserva.id),
                  _ordenOriginal: index,
                };
              }
              throw err;
            }
          }),
        );

        if (!cancelado) setReservas(ordenarReservas(enriquecidas));
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

  const totalPaginas = Math.max(Math.ceil(reservas.length / PAGE_SIZE), 1);
  const reservasPagina = useMemo(
    () =>
      reservas.slice(
        (paginaActual - 1) * PAGE_SIZE,
        paginaActual * PAGE_SIZE,
      ),
    [paginaActual, reservas],
  );

  const focusReserva =
    !cargando && focusId && !focusConsumido
      ? reservas.find((item) => item.id === focusId)
      : undefined;

  const reservaModal =
    reservas.find((item) => item.id === reservaSeleccionadaId) ||
    focusReserva ||
    null;
  const verificandoCheckinModal =
    Boolean(reservaModal) && reservasVerificandoCheckin.has(reservaModal.id);

  const marcarVerificandoCheckin = (reservaId, verificando) => {
    setReservasVerificandoCheckin((prev) => {
      const siguiente = new Set(prev);
      if (verificando) {
        siguiente.add(reservaId);
      } else {
        siguiente.delete(reservaId);
      }
      return siguiente;
    });
  };

  const actualizarReservaConCheckin = async (reserva) => {
    if (!puedeHacerCheckin(reserva)) return;

    marcarVerificandoCheckin(reserva.id, true);
    try {
      const checkin = await obtenerMiCheckinPorReserva(reserva.id);
      setReservas((prev) =>
        ordenarReservas(
          prev.map((item) =>
            item.id === reserva.id ? { ...item, checkin } : item,
          ),
        ),
      );
    } catch (err) {
      if (err.response?.status === 404) {
        const checkin = checkinRecordado(reserva.id);
        setReservas((prev) =>
          ordenarReservas(
            prev.map((item) =>
              item.id === reserva.id ? { ...item, checkin } : item,
            ),
          ),
        );
        return;
      }
      setError(err.response?.data?.detail || "No se pudo verificar el check-in.");
    } finally {
      marcarVerificandoCheckin(reserva.id, false);
    }
  };

  const abrirReserva = (reserva) => {
    if (puedeHacerCheckin(reserva)) {
      actualizarReservaConCheckin(reserva);
    }
    setReservaSeleccionadaId(reserva.id);
  };

  useEffect(() => {
    if (!focusReserva) return;
    const indice = reservas.findIndex((item) => item.id === focusReserva.id);
    const paginaFocus = Math.floor(indice / PAGE_SIZE) + 1;
    if (indice >= 0 && paginaFocus !== paginaActual) {
      const proximo = new URLSearchParams(searchParams);
      proximo.set("page", String(paginaFocus));
      setSearchParams(proximo, { replace: true });
      return;
    }

    const nodo = reservaRefs.current[focusReserva.id];
    if (nodo) {
      nodo.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [focusReserva, paginaActual, reservas, searchParams, setSearchParams]);

  const cambiarPagina = (proximaPagina) => {
    const proximo = new URLSearchParams(searchParams);
    proximo.set("page", String(proximaPagina));
    proximo.delete("focus");
    setSearchParams(proximo);
    setFocusConsumido(true);
  };

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
          <>
            <div className="grid gap-4">
              {reservasPagina.map((reserva) => {
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
                    onClick={() => abrirReserva(reserva)}
                    className={`grid w-full gap-4 rounded-[24px] border bg-autospot-white p-5 text-left shadow-[0_18px_50px_rgba(15,23,42,0.07)] transition hover:border-autospot-accent sm:grid-cols-[1.3fr_0.9fr_auto] sm:items-center ${estaFocus
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

            <Paginacion
              page={paginaActual}
              pages={totalPaginas}
              total={reservas.length}
              onChange={cambiarPagina}
            />
          </>
        )}
      </section>

      <ReservaCodigoModal
        reserva={reservaModal}
        verificandoCheckin={verificandoCheckinModal}
        onClose={cerrarModal}
      />
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

const Paginacion = ({ page, pages, total, onChange }) => (
  <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
    <p className="text-sm font-semibold text-autospot-muted">
      {total} reserva{total === 1 ? "" : "s"}
    </p>
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
        className="inline-flex h-10 items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 text-sm font-bold text-autospot-black transition hover:border-autospot-accent disabled:cursor-not-allowed disabled:opacity-45"
      >
        <ChevronLeft className="h-4 w-4" aria-hidden="true" />
        Anterior
      </button>
      <span className="px-2 text-sm font-bold text-autospot-muted">
        {page} / {pages}
      </span>
      <button
        type="button"
        onClick={() => onChange(page + 1)}
        disabled={page >= pages}
        className="inline-flex h-10 items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 text-sm font-bold text-autospot-black transition hover:border-autospot-accent disabled:cursor-not-allowed disabled:opacity-45"
      >
        Siguiente
        <ChevronRight className="h-4 w-4" aria-hidden="true" />
      </button>
    </div>
  </div>
);

export default MisReservasPage;
