import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { listarMisAlquileres } from "../api/reservasService";
import { formatearFechaHora, formatearMonto } from "../utils/reservaFormatters";

const PAGE_SIZE = 10;

const ESTADO_UI = {
  EN_CURSO: {
    label: "En curso",
    action: "Ver y entregar",
    className: "bg-[#dcfce7] text-[#166534] border border-[#bbf7d0]",
  },
  ENTREGA_SOLICITADA: {
    label: "Esperando recepción",
    action: "Ver detalle",
    className: "bg-[#fef3c7] text-[#92400e] border border-[#fde68a]",
  },
  DEVUELTO: {
    label: "Recibido",
    action: "Ver detalle",
    className: "bg-[#dcfce7] text-[#166534] border border-[#bbf7d0]",
  },
  CHECKOUT_PENDIENTE: {
    label: "Checkout realizado",
    action: "Revisar checkout",
    className: "bg-[#dbeafe] text-[#1d4ed8] border border-[#bfdbfe]",
  },
  FINALIZADA: {
    label: "Finalizado",
    action: "Ver historial",
    className: "bg-white text-autospot-muted border border-autospot-border",
  },
};

const obtenerEstadoUi = (estado) =>
  ESTADO_UI[(estado || "").toUpperCase()] || {
    label: estado || "Sin estado",
    action: "Ver detalle",
    className: "bg-autospot-cream text-autospot-muted border border-autospot-border",
  };

const MisAlquileresPage = () => {
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
        const data = await listarMisAlquileres({ page, size: PAGE_SIZE });
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
          setError(err.response?.data?.detail || "No se pudieron cargar tus alquileres.");
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
            Cliente
          </p>
          <h1 className="font-display text-3xl font-black tracking-[-0.05em] text-autospot-black sm:text-4xl">
            Mis alquileres
          </h1>
        </div>
        <Link
          to="/catalogo"
          className="inline-flex justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
        >
          Buscar autos
        </Link>
      </div>

      {cargando && (
        <div className="overflow-hidden rounded-2xl border border-autospot-border bg-autospot-white">
          {[0, 1, 2, 3].map((item) => (
            <div key={item} className="h-20 animate-pulse border-b border-autospot-border bg-white/50 last:border-b-0" />
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
            Todavía no tenés alquileres
          </h2>
          <Link
            to="/catalogo"
            className="mt-6 inline-flex rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
          >
            Ver catálogo
          </Link>
        </div>
      )}

      {!cargando && !error && pagina.items.length > 0 && (
        <>
          <div className="overflow-hidden rounded-2xl border border-autospot-border bg-autospot-white">
            {pagina.items.map((alquiler) => {
              const vehiculo = alquiler.vehiculo;
              const estado = obtenerEstadoUi(alquiler.estado);
              const estaFocus = focusId === alquiler.id;

              return (
                <Link
                  key={alquiler.id}
                  ref={(nodo) => {
                    if (nodo) {
                      itemRefs.current[alquiler.id] = nodo;
                    } else {
                      delete itemRefs.current[alquiler.id];
                    }
                  }}
                  to={`/usuario/alquileres/${alquiler.id}`}
                  className={`grid gap-4 border-b border-autospot-border px-4 py-4 text-left transition last:border-b-0 hover:bg-[#fafaf9] sm:grid-cols-[1.1fr_1.4fr_auto] sm:items-center sm:px-5 ${
                    estaFocus ? "bg-[#fafaf9] ring-2 ring-inset ring-autospot-accent/35" : ""
                  }`}
                >
                  <div className="min-w-0">
                    <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-accent">
                      {alquiler.codigo_reserva}
                    </p>
                    <h2 className="mt-1 truncate font-display text-lg font-black tracking-[-0.04em] text-autospot-black">
                      {vehiculo?.marca} {vehiculo?.modelo}
                    </h2>
                    <p className="mt-1 truncate text-sm text-autospot-muted">
                      {vehiculo?.patente || "Sin patente"} · {alquiler.estacion_retiro}
                    </p>
                  </div>

                  <dl className="grid gap-3 text-sm sm:grid-cols-3">
                    <Dato label="Inicio" valor={formatearFechaHora(alquiler.fecha_inicio)} />
                    <Dato label="Fin" valor={formatearFechaHora(alquiler.fecha_fin)} />
                    <Dato label="Total" valor={formatearMonto(alquiler.monto_total)} />
                  </dl>

                  <div className="flex items-center justify-between gap-3 sm:justify-end">
                    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${estado.className}`}>
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

const Dato = ({ label, valor }) => (
  <div className="min-w-0">
    <dt className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
      {label}
    </dt>
    <dd className="truncate font-bold text-autospot-black">{valor || "—"}</dd>
  </div>
);

export default MisAlquileresPage;
