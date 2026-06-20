import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { listarRecepcionAutos } from "../../reservas/api/reservasService";
import { formatearEstado } from "../../../utils/formatStatus";
import {
  formatearFechaHora,
  formatearMonto,
} from "../../reservas/utils/reservaFormatters";

const PAGE_SIZE = 10;

const ESTADO_UI = {
  ENTREGA_SOLICITADA: {
    label: "Pendiente de recepción",
    action: "Registrar entrada",
    className: "bg-[#fef3c7] text-[#92400e] border border-[#fde68a]",
  },
  DEVUELTO: {
    label: "Falta checkout",
    action: "Hacer checkout",
    className: "bg-[#dcfce7] text-[#166534] border border-[#bbf7d0]",
  },
  CHECKOUT_PENDIENTE: {
    label: "Checkout enviado",
    action: "Ver checkout",
    className: "bg-[#dbeafe] text-[#1d4ed8] border border-[#bfdbfe]",
  },
  FINALIZADA: {
    label: "Finalizado",
    action: "Ver historial",
    className: "bg-[#dcfce7] text-[#166534] border border-[#bbf7d0]",
  },
};

const obtenerEstadoUi = (estado) =>
  ESTADO_UI[(estado || "").toUpperCase()] || {
    label: formatearEstado(estado),
    action: "Ver detalle",
    className:
      "bg-autospot-cream text-autospot-muted border border-autospot-border",
  };

const RecepcionAutosPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const pageParam = Number(searchParams.get("page") || "1");
  const focusId = searchParams.get("focus");
  const page = Number.isFinite(pageParam) && pageParam > 0 ? pageParam : 1;

  const [pagina, setPagina] = useState({
    items: [],
    total: 0,
    page,
    size: PAGE_SIZE,
    pages: 0,
  });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const itemRefs = useRef({});

  useEffect(() => {
    let cancelado = false;

    const cargar = async () => {
      setCargando(true);
      setError("");

      try {
        const data = await listarRecepcionAutos({ page, size: PAGE_SIZE });
        if (!cancelado) {
          setPagina({
            items: Array.isArray(data.items) ? data.items : [],
            total: data.total || 0,
            page: data.page || page,
            size: data.size || PAGE_SIZE,
            pages: data.pages || 0,
          });
        }
      } catch (err) {
        if (!cancelado) {
          setError(
            err.response?.data?.detail || "No se pudo cargar la recepción.",
          );
        }
      } finally {
        if (!cancelado) setCargando(false);
      }
    };

    cargar();

    return () => {
      cancelado = true;
    };
  }, [page]);

  useEffect(() => {
    if (cargando || !focusId) return;
    const nodo = itemRefs.current[focusId];
    if (nodo) {
      nodo.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [cargando, focusId, pagina.items]);

  const cambiarPagina = (proxima) => {
    const params = new URLSearchParams(searchParams);
    params.set("page", String(proxima));
    params.delete("focus");
    setSearchParams(params);
  };

  return (
    <section className="w-full min-w-0">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
            Administración
          </p>
          <h1 className="font-display text-3xl font-black tracking-[-0.05em] text-autospot-black sm:text-4xl">
            Recepción de autos
          </h1>
        </div>
      </div>

      {cargando && (
        <div className="overflow-hidden rounded-2xl border border-autospot-border bg-autospot-white">
          {[0, 1, 2, 3].map((item) => (
            <div
              key={item}
              className="h-20 animate-pulse border-b border-autospot-border bg-white/50 last:border-b-0"
            />
          ))}
        </div>
      )}

      {!cargando && error && (
        <div className="rounded-2xl border border-autospot-border bg-autospot-cream/60 p-5 text-sm font-semibold text-autospot-black">
          {error}
        </div>
      )}

      {!cargando && !error && pagina.items.length === 0 && (
        <div className="rounded-2xl border border-autospot-border bg-autospot-white p-8 text-center">
          <h2 className="font-display text-2xl font-black tracking-[-0.04em] text-autospot-black">
            No hay autos para recibir
          </h2>
        </div>
      )}

      {!cargando && !error && pagina.items.length > 0 && (
        <>
          <div className="overflow-hidden rounded-2xl border border-autospot-border bg-autospot-white">
            <div className="hidden grid-cols-[1.15fr_1fr_1fr_1fr_auto] gap-4 border-b border-autospot-border bg-[#fafaf9] px-5 py-3 text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-muted lg:grid">
              <span>Auto</span>
              <span>Reserva</span>
              <span>Recepción</span>
              <span>Importes</span>
              <span className="text-right">Estado</span>
            </div>

            {pagina.items.map((reserva) => {
              const vehiculo = reserva.vehiculo;
              const estado = obtenerEstadoUi(reserva.estado);
              const estaFocus = focusId === reserva.id;

              return (
                <Link
                  key={reserva.id}
                  ref={(nodo) => {
                    if (nodo) {
                      itemRefs.current[reserva.id] = nodo;
                    } else {
                      delete itemRefs.current[reserva.id];
                    }
                  }}
                  to={`/admin/recepcion/${reserva.id}`}
                  className={`grid gap-4 border-b border-autospot-border px-4 py-4 transition last:border-b-0 hover:bg-[#fafaf9] lg:grid-cols-[1.15fr_1fr_1fr_1fr_auto] lg:items-center lg:px-5 ${
                    estaFocus
                      ? "bg-[#fafaf9] ring-2 ring-inset ring-autospot-accent/35"
                      : ""
                  }`}
                >
                  <div className="min-w-0">
                    <p className="truncate font-display text-lg font-black tracking-[-0.04em] text-autospot-black">
                      {vehiculo?.marca} {vehiculo?.modelo}
                    </p>
                    <p className="mt-1 truncate text-sm text-autospot-muted">
                      {vehiculo?.patente || "Sin patente"} ·{" "}
                      {reserva.estacion_retiro}
                    </p>
                  </div>

                  <div className="min-w-0">
                    <p className="text-xl font-bold uppercase  text-autospot-accent">
                      {reserva.codigo_reserva}
                    </p>
                  </div>

                  <div className="text-sm">
                    <p className="font-bold text-autospot-black">
                      {formatearFechaHora(reserva.fecha_devolucion_real)}
                    </p>
                    <p className="mt-1 text-autospot-muted">
                      Aviso:{" "}
                      {formatearFechaHora(reserva.fecha_entrega_solicitada)}
                    </p>
                  </div>

                  <div className="text-sm">
                    <p className="font-bold text-autospot-black">
                      {formatearMonto(reserva.monto_total)}
                    </p>
                    <p className="mt-1 text-autospot-muted">Total</p>
                  </div>

                  <div className="flex items-center justify-between gap-3 lg:justify-end">
                    <span
                      className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${estado.className}`}
                    >
                      {estado.label}
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-sm font-bold text-autospot-accent">
                      {estado.action}
                      <ChevronRight className="h-4 w-4" strokeWidth={2.4} />
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>

          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm font-semibold text-autospot-muted">
              {pagina.total} alquiler{pagina.total === 1 ? "" : "es"}
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => cambiarPagina(page - 1)}
                disabled={page <= 1}
                className="inline-flex h-10 items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 text-sm font-bold text-autospot-black transition hover:border-autospot-accent disabled:cursor-not-allowed disabled:opacity-45"
              >
                <ChevronLeft className="h-4 w-4" />
                Anterior
              </button>
              <span className="px-2 text-sm font-bold text-autospot-muted">
                {page} / {Math.max(pagina.pages, 1)}
              </span>
              <button
                type="button"
                onClick={() => cambiarPagina(page + 1)}
                disabled={page >= pagina.pages}
                className="inline-flex h-10 items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 text-sm font-bold text-autospot-black transition hover:border-autospot-accent disabled:cursor-not-allowed disabled:opacity-45"
              >
                Siguiente
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </section>
  );
};

export default RecepcionAutosPage;
