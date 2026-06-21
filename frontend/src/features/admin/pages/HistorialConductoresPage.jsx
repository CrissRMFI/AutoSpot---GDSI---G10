import { useCallback, useEffect, useState } from "react";
import { Search, Car, Calendar, MapPin, DollarSign, Inbox } from "lucide-react";
import { getHistorialConductores } from "../api/historialConductoresApi";
import { formatearEstado } from "../../../utils/formatStatus";

const HistorialConductoresPage = () => {
  const [conductores, setConductores] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [busqueda, setBusqueda] = useState("");
  const [expandido, setExpandido] = useState(null);

  useEffect(() => {
    let cancelado = false;

    const cargar = async () => {
      setCargando(true);
      setError(null);
      try {
        const data = await getHistorialConductores();
        if (!cancelado) setConductores(Array.isArray(data) ? data : []);
      } catch {
        if (!cancelado) setError("No se pudo cargar el historial de conductores.");
      } finally {
        if (!cancelado) setCargando(false);
      }
    };

    cargar();
    return () => {
      cancelado = true;
    };
  }, []);

  const conductoresFiltrados = conductores.filter((c) => {
    if (!busqueda.trim()) return true;
    const termino = busqueda.toLowerCase().trim();
    const nombre = `${c.nombre || ""} ${c.apellido || ""}`.toLowerCase();
    return (
      (c.email || "").toLowerCase().includes(termino) ||
      nombre.includes(termino) ||
      (c.dni || "").includes(termino)
    );
  });

  const toggleExpandido = useCallback((id) => {
    setExpandido((prev) => (prev === id ? null : id));
  }, []);

  const formatearFecha = (iso) => {
    if (!iso) return "—";
    return new Date(iso).toLocaleDateString("es-AR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const formatearMonto = (monto) => {
    if (monto == null) return "—";
    return Number(monto).toLocaleString("es-AR", {
      style: "currency",
      currency: "ARS",
      minimumFractionDigits: 0,
    });
  };

  return (
    <section className="w-full min-w-0">
      {/* Header */}
      <div className="mb-6 min-w-0">
        <h1 className="text-3xl font-black leading-tight text-autospot-black sm:text-4xl">
          Historial de conductores
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-autospot-muted">
          Consultá los antecedentes y alquileres de cada conductor registrado
          en la plataforma.
        </p>
      </div>

      {/* Buscador */}
      <div className="mb-6">
        <div className="relative max-w-lg">
          <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-autospot-muted">
            <Search className="h-4 w-4" aria-hidden="true" />
          </span>
          <input
            id="busqueda-conductor"
            type="text"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar por nombre, email o DNI…"
            className="w-full rounded-xl border border-autospot-border bg-autospot-white py-3 pl-11 pr-4 text-sm text-autospot-black placeholder:text-autospot-muted/60 focus:border-autospot-accent focus:outline-2 focus:outline-autospot-accent/20"
          />
        </div>
      </div>

      {/* Estados */}
      {cargando && (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent" />
        </div>
      )}

      {error && !cargando && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-5 py-4 text-sm font-bold text-red-700">
          {error}
        </div>
      )}

      {/* Empty State (CA 3) */}
      {!cargando && !error && conductoresFiltrados.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-autospot-border bg-autospot-white px-6 py-16 text-center">
          <span className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-full bg-[#efe9df]">
            <Inbox className="h-8 w-8 text-autospot-accent" aria-hidden="true" />
          </span>
          <h3 className="text-lg font-black text-autospot-black">
            Sin resultados
          </h3>
          <p className="mt-2 max-w-sm text-sm text-autospot-muted">
            {busqueda.trim()
              ? `No se encontraron conductores que coincidan con "${busqueda}".`
              : "No hay conductores con alquileres registrados en la plataforma."}
          </p>
        </div>
      )}

      {/* Lista de conductores */}
      {!cargando && !error && conductoresFiltrados.length > 0 && (
        <div className="space-y-4">
          {conductoresFiltrados.map((conductor) => (
            <article
              key={conductor.id}
              className="overflow-hidden rounded-xl border border-autospot-border bg-autospot-white transition-shadow hover:shadow-autospot-soft"
            >
              {/* Cabecera del conductor */}
              <button
                type="button"
                onClick={() => toggleExpandido(conductor.id)}
                className="flex w-full items-center gap-4 appearance-none border-none bg-transparent px-5 py-4 text-left outline-none transition hover:bg-[#fafaf9] focus:bg-[#fafaf9] focus:outline-none"
                aria-expanded={expandido === conductor.id}
              >
                <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-autospot-accent text-sm font-bold text-white">
                  {(conductor.nombre?.[0] || conductor.email?.[0] || "?").toUpperCase()}
                  {(conductor.apellido?.[0] || "").toUpperCase()}
                </span>

                <div className="min-w-0 flex-1">
                  <h3 className="truncate text-sm font-black text-autospot-black">
                    {conductor.nombre && conductor.apellido
                      ? `${conductor.nombre} ${conductor.apellido}`
                      : conductor.email}
                  </h3>
                  <div className="mt-0.5 flex flex-wrap items-center gap-x-4 gap-y-0.5 text-xs text-autospot-muted">
                    <span>{conductor.email}</span>
                    {conductor.dni && <span>DNI: {conductor.dni}</span>}
                  </div>
                </div>

                <div className="flex shrink-0 items-center gap-3">
                  <span className="hidden items-center gap-1.5 rounded-full bg-[#efe9df] px-3 py-1 text-xs font-bold text-autospot-accent sm:inline-flex">
                    <Car className="h-3.5 w-3.5" aria-hidden="true" />
                    {conductor.alquileres?.length || 0} alquiler
                    {(conductor.alquileres?.length || 0) !== 1 ? "es" : ""}
                  </span>

                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className={`h-5 w-5 text-autospot-muted transition-transform ${expandido === conductor.id ? "rotate-180" : ""
                      }`}
                    aria-hidden="true"
                  >
                    <path d="M6 9l6 6 6-6" />
                  </svg>
                </div>
              </button>

              {/* Detalle de alquileres (expandible) */}
              {expandido === conductor.id && (
                <div className="border-t border-autospot-border bg-[#fafaf9] px-5 py-4">
                  {conductor.alquileres?.length > 0 ? (
                    <div className="space-y-3">
                      {conductor.alquileres.map((alq) => (
                        <div
                          key={alq.id}
                          className="rounded-xl border border-autospot-border bg-autospot-white p-4"
                        >
                          <div className="flex flex-wrap items-start justify-between gap-2">
                            <div className="min-w-0">
                              <p className="text-sm font-black text-autospot-black">
                                {alq.vehiculo_marca || "—"} {alq.vehiculo_modelo || ""}
                              </p>
                              {alq.vehiculo_patente && (
                                <p className="mt-0.5 text-xs text-autospot-muted">
                                  Patente: {alq.vehiculo_patente}
                                </p>
                              )}
                            </div>
                            <span
                              className={`inline-flex shrink-0 rounded-full px-2.5 py-0.5 text-xs font-bold ${alq.estado === "FINALIZADA"
                                  ? "bg-green-100 text-green-700"
                                  : alq.estado === "CONFIRMADA"
                                    ? "bg-blue-100 text-blue-700"
                                    : alq.estado === "RECHAZADA"
                                      ? "bg-red-100 text-red-700"
                                      : "bg-amber-100 text-amber-700"
                                }`}
                            >
                              {formatearEstado(alq.estado)}
                            </span>
                          </div>

                          <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1.5 text-xs text-autospot-muted">
                            <span className="inline-flex items-center gap-1">
                              <Calendar className="h-3.5 w-3.5" aria-hidden="true" />
                              {formatearFecha(alq.fecha_inicio)} – {formatearFecha(alq.fecha_fin)}
                            </span>
                            <span className="inline-flex items-center gap-1">
                              <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                              {alq.estacion_retiro}
                            </span>
                            <span className="inline-flex items-center gap-1">
                              <DollarSign className="h-3.5 w-3.5" aria-hidden="true" />
                              {formatearMonto(alq.monto_total)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-autospot-muted">
                      Este conductor no tiene alquileres registrados.
                    </p>
                  )}
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
};

export default HistorialConductoresPage;
